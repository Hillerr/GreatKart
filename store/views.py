from django.contrib import messages
from store.forms import ReviewForm
from django.core import paginator
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, ReviewRating
from orders.models import OrderProduct
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None 

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        product_count = products.count()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': product_count
    }

    return render(request, 'store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    try:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    except OrderProduct.DoesNotExists:
        orderproduct = None

    # Get reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews
    }
    
    return render(request, 'product-detail.html', context)


def search(request):
    keyword = request.GET.get('keyword')
    
    if keyword:
        products = Product.objects.order_by('-created_date').filter(
            Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
        product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
        'keyword': keyword
    }

    return render(request, 'store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Obrigado! Sua opinião foi atualizada')

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)

            if form.is_valid():
                print('form is valid')
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Obrigado pela sua avaliação')

            else:
                print('not a valid form')
    
    return redirect(url)