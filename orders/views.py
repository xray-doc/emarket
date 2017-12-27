from django.http import JsonResponse
from .models import ProductInBasket


def basket_list(request):
    session_key = request.session.session_key

    return_dict = {}

    if request.method == "POST":
        data = request.POST
        product_id = data.get("product_id")
        nmb = data.get("nmb")

        new_product, created = ProductInBasket.objects.get_or_create(session_key=session_key, product_id=product_id, defaults={"nmb": nmb})
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    elif request.GET.get("remove_product_id"):
        ProductInBasket.objects.get(id=request.GET.get("remove_product_id")).delete()

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