from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User

from .models import *
from .forms import *



def update_basket_list(request):
    """
    Renders navbar basket list HTML
    """
    session_key = request.session.session_key
    user = request.user

    if request.method == "POST":
        data = request.POST
    else:
        data = request.GET

    # Adding product to basket
    if data.get("product_id"):
        product_id = data.get("product_id")
        nmb = data.get("nmb") or 1

        if user.is_authenticated():
            # if user is authenticated product in basket binds to user object,
            # else to session_key
            new_product, created = ProductInBasket.objects.get_or_create(user=user,
                                                                         product_id=product_id,
                                                                         defaults={"nmb": nmb})
        else:
            new_product, created = ProductInBasket.objects.get_or_create(session_key=session_key,
                                                                         product_id=product_id,
                                                                         defaults={"nmb": nmb})
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    # Removing product from basket
    if data.get("remove_product_id"):
        ProductInBasket.objects.get(id=request.GET.get("remove_product_id")).delete()

    # Getting basket list
    if user.is_authenticated():
        # if user is authenticated product in basket binds to user object,
        # else to session_key
        products_in_basket = ProductInBasket.objects.filter(user=user, is_active=True)
        products_total_price = ProductInBasket.get_basket_total_price(user=user)
    else:
        products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)
        products_total_price = ProductInBasket.get_basket_total_price(session_key=session_key)

    products_total_nmb = products_in_basket.count()
    products_in_basket_ids = ''
    for product_in_basket in products_in_basket:
        products_in_basket_ids += str(product_in_basket.product.id) + ','

    return render(request, 'basket_items_list.html', locals())


def changeProductInBasket(request):
    session_key = request.session.session_key
    user = request.user

    return_dict = {}
    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")

    if user.is_authenticated():
        product = ProductInBasket.objects.get(user=user, id=product_id)
    else:
        product = ProductInBasket.objects.get(session_key=session_key, id=product_id)

    product.nmb = int(nmb)
    product.save(force_update=True)
    return_dict["total_product_price"] = product.total_price

    return JsonResponse(return_dict)



def checkout(request):
    """
    Creating order
    """
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
