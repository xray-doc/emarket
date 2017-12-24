from django.shortcuts import render
from .models import *



def product(request, product_id):
    product = Product.objects.get(pk=product_id)


    session_key = request.session.session_key
    if not session_key:
        request.session.cycle_key()


    return render(request, 'products/product.html', locals())