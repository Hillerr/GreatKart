from orders.models import Order
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from carts.models import CartItem, Cart
from .forms import OrderForm
import datetime


# Create your views here.
def payment(request):
    return render(request, 'orders/payment.html')


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