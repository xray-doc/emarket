from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView, View

from .models import *
from .forms import *
from accounts.models import Profile


class UpdateBasketList(TemplateView):

    template_name = 'basket_items_list.html'

    def post(self, request, *args, **kwargs):
        data = request.POST
        session_key = request.session.session_key
        user = request.user

        # Adding product to basket by product id
        product_id = data.get("product_id")
        if product_id:
            nmb = data.get("nmb") or 1

            if user.is_authenticated():
                # if user is authenticated, then product in basket assigns to user object,
                # else to session_key
                ProductInBasket.add_product_to_basket(user=user, product_id=product_id, nmb=nmb)
            else:
                ProductInBasket.add_product_to_basket(session_key=session_key, product_id=product_id, nmb=nmb)

        # Removing product from basket
        rm_product_id = data.get('remove_product_id')
        if rm_product_id:
            if user.is_authenticated():
                ProductInBasket.remove_product_from_basket(user=user, rm_product_id=rm_product_id)
            else:
                ProductInBasket.remove_product_from_basket(session_key=session_key, rm_product_id=rm_product_id)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        session_key = request.session.session_key
        user = request.user

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


def changeProductInBasketQuantity(request):
    session_key = request.session.session_key
    user = request.user

    return_dict = {}
    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")

    if user.is_authenticated():
        product = ProductInBasket.objects.get(user=user, product=product_id)
    else:
        product = ProductInBasket.objects.get(session_key=session_key, product=product_id)

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

        context = dict()
        if user.is_authenticated():
            order.user = user
            context['user_profile_url'] = user.profile_set.first().get_absolute_url()

        for product_in_basket in products_in_basket:
            ProductInOrder.objects.create(
                order = order,
                product = product_in_basket.product,
                nmb = product_in_basket.nmb,
                price_per_item = product_in_basket.price_per_item,
            )

        return render(request, 'orders/done.html', context)

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
