from django.shortcuts import render
from products.models import *



def main(request):
    ios_devices = Product.objects.filter(os__name='iOS')
    android_devices = Product.objects.filter(os__name='Android')

    return render(request, 'home.html', locals())



def delivery(request):
    return render(request, 'delivery.html', locals())



def contacts(request):
    return render(request, 'contacts.html', locals())