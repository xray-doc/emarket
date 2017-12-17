from django.shortcuts import render
from .models import *



def product(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render(request, 'products/product.html', locals())