from orders.models import Order, OrderProduct, Payment
from store.models import Product
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from carts.models import CartItem, Cart
from .forms import OrderForm
import datetime
import json 


# Create your views here.
def payment(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    # Create a new payment object 
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True 
    order.save()

    # Move the cart items to Order Products table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # Decrease the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity

    # Clear the cart
    CartItem.objects.filter(user=request.user).delete()


    # Send order number and transaction ID back to the frontend
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }


    return JsonResponse(data)

def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to zero, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2*total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            #Store all the information inside Order Table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.zip_code = form.cleaned_data['zip_code']
            data.order_note = form.cleaned_data['order_note']
            data.complement = form.cleaned_data['complement']
            data.order_total =  grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            today = datetime.date.today()
            dt = int(today.strftime('%d'))
            mt = int(today.strftime('%m'))
            yr = int(today.strftime('%Y'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'tax': tax,
                'grand_total': grand_total
            }

            return render(request, 'orders/payments.html', context)

    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transaction_id = request.GET.get('payment_ID')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'subtotal': order.order_total - order.tax
        }

        return render(request, 'orders/order_complete.html', context)

    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')