from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User

from .models import *
from .forms import *



def basket_list(request):
    session_key = request.session.session_key
    return_dict = {}

    if request.method == "POST":
        data = request.POST
    else:
        data = request.GET

    # Adding product to basket
    if data.get("product_id"):
        product_id = data.get("product_id")
        nmb = data.get("nmb") or 1

        new_product, created = ProductInBasket.objects.get_or_create(session_key=session_key, product_id=product_id,
                                                                     defaults={"nmb": nmb})
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    # Removing product from basket
    if data.get("remove_product_id"):
        ProductInBasket.objects.get(id=request.GET.get("remove_product_id")).delete()

    # Getting basket list
    products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)
    products_total_nmb = products_in_basket.count()
    products_total_price = ProductInBasket.get_basket_total_price(session_key)

    return_dict["products_total_nmb"] = products_total_nmb
    return_dict["products_total_price"] = products_total_price

    return_dict["products"] = []
    for item in products_in_basket:
        product_dict = {}
        product_dict["name"] = item.product.name
        product_dict["price_per_item"] = item.price_per_item
        product_dict["nmb"] = item.nmb
        product_dict["id"] = item.id
        return_dict["products"].append(product_dict)

    return JsonResponse(return_dict)



def changeProductInBasket(request):
    session_key = request.session.session_key
    return_dict = {}
    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")
    product = ProductInBasket.objects.get(session_key=session_key, id=product_id)
    product.nmb = int(nmb)
    product.save(force_update=True)
    return_dict["total_product_price"] = product.total_price

    return JsonResponse(return_dict)



def checkout(request):
    session_key = request.session.session_key
    products_in_basket = ProductInBasket.objects.filter(session_key=session_key)
    products_total_price = ProductInBasket.get_basket_total_price(session_key)

    form = CheckoutContactForm(request.POST or None)
    if request.POST and form.is_valid():
        data = request.POST
        name = data["name"]
        phone = data["phone"]
        email = data["email"]
        address = data["address"]
        comments = data["comments"]

        user, created = User.objects.get_or_create(username=phone, defaults={"first_name": name})
        order = Order.objects.create(
            user=user,
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            customer_address=address,
            comments=comments,
            status_id=1
        )

        for product_in_basket in products_in_basket:
            ProductInOrder.objects.create(
                order = order,
                product = product_in_basket.product,
                nmb = product_in_basket.nmb,
                price_per_item = product_in_basket.price_per_item,
            )

        return render(request, 'orders/done.html', locals())

    return render(request, 'orders/checkout.html', locals())
