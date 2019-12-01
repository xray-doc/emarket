from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView, View

from .models import *
from .forms import *
from accounts.models import Profile


#This class-based view should substitute the function below.
#It is not used yet.
class UpdateBasketList(TemplateView):

    template_name = 'basket_items_list.html'

    def post(self, request, *args, **kwargs):
        data = request.POST

        if data.get("product_id"):
            request = self.request
            session_key = request.session.session_key
            user = request.user

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

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = request.GET

        if data.get("remove_product_id"):
            ProductInBasket.objects.get(id=request.GET.get("remove_product_id")).delete()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        request = self.request
        session_key = request.session.session_key
        user = request.user
        context = {}

        if user.is_authenticated():
            current_user_or_session_key = {'user': user}
        else:
            current_user_or_session_key = {'session_key': session_key}

        products_in_basket = ProductInBasket.objects.filter(is_active=True, **current_user_or_session_key)
        products_total_price = ProductInBasket.get_basket_total_price(**current_user_or_session_key)

        products_total_nmb = products_in_basket.count()
        products_in_basket_ids = ''
        for product_in_basket in products_in_basket:
            products_in_basket_ids += str(product_in_basket.product.id) + ','

        context = {
            'user': user,
            'products_in_basket': products_in_basket,
            'products_total_price': products_total_price,
            'products_total_nmb': products_total_nmb,
            'products_in_basket_ids': products_in_basket_ids
        }

        return context


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
    # TODO: it should be post query
    if data.get("remove_product_id"):
        ProductInBasket.objects.get(id=request.GET.get("remove_product_id")).delete()

    if user.is_authenticated():
        current_user_or_session_key = {'user': user}
    else:
        current_user_or_session_key = {'session_key': session_key}

    products_in_basket = ProductInBasket.objects.filter(is_active=True, **current_user_or_session_key)
    products_total_price = ProductInBasket.get_basket_total_price(**current_user_or_session_key)

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
    user = request.user

    if user.is_authenticated():
        products_in_basket = ProductInBasket.objects.filter(user=user)
        products_total_price = ProductInBasket.get_basket_total_price(user=user)
    else:
        products_in_basket = ProductInBasket.objects.filter(session_key=session_key)
        products_total_price = ProductInBasket.get_basket_total_price(session_key=session_key)

    form = CheckoutContactForm(request.POST or None)
    if request.POST and form.is_valid():
        data = request.POST
        name = data["name"]
        phone = data["phone"]
        email = data["email"]
        address = data["address"]
        comments = data["comments"]

        #user, created = User.objects.get_or_create(username=phone, defaults={"first_name": name})
        order = Order.objects.create(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            customer_address=address,
            comments=comments,
            status_id=1
        )

        if user.is_authenticated():
            order.user = user

        for product_in_basket in products_in_basket:
            ProductInOrder.objects.create(
                order = order,
                product = product_in_basket.product,
                nmb = product_in_basket.nmb,
                price_per_item = product_in_basket.price_per_item,
            )

        #TODO: change to success page
        return render(request, 'orders/done.html', locals())

    profile = None
    if user.is_authenticated():
        profile = Profile.objects.filter(user=user).first()

    if profile is not None:
        name = profile.get_full_name()
        phone = profile.phone
        email = user.email
        address = profile.address
    else:
        name = request.POST.get('name', None)
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        address = request.POST.get('address', None)


    return render(request, 'orders/checkout.html', locals())
