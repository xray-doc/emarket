from django.shortcuts import render
from products.models import *



def home(request):
    products_images = ProductImage.objects.filter(is_active=True, is_main=True)
    return render(request, 'home.html', locals())
