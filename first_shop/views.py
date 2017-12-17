from django.shortcuts import render
from products.models import *



def home(request):
    osList = [
        'iOS',
        'Android'
    ]

    devices_list = []
    for os in osList:
        devices = []
        for device in Product.objects.filter(os__name=os):
            img = ProductImage.objects.get(product=device, is_main=True)
            devices.append({'device': device, 'img': img})
        devices_list.append([os, devices])


    return render(request, 'home.html', locals())


0