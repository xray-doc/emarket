from .models import ProductInBasket


def getting_basket_info(request):
    """
    Info about product user have already added to basket
    (products, number of each, total price)
    """
    session_key = request.session.session_key
    if not session_key:
        request.session.cycle_key()

    products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)
    products_total_nmb = products_in_basket.count()
    get_basket_total_price = ProductInBasket.get_basket_total_price(session_key=session_key)

    return locals()