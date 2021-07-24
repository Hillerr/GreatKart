from category.models import Category
from django.shortcuts import redirect
from store.models import Product
from store import urls

def home(request):
    return redirect('store')