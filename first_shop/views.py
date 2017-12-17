from django.shortcuts import render
from products.models import *



def home(request):
    ios_devices = Product.objects.filter(os__name='iOS')
    android_devices = Product.objects.filter(os__name='Android')

    return render(request, 'home.html', locals())


