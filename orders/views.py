from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse

from accounts.models import Profile
from .models import Status, Order, ProductInBasket, ProductInOrder
from .forms import OrderForm


class UpdateBasketList(TemplateView):
    """
    This view accepts post request with product_id and nmb of products to add to basket
    or remove_product_id to remove from basket.
    Returns html response for inserting into basket list in navbar.
    """

    template_name = 'basket_items_list.html'

    def post(self, request, *args, **kwargs):
        data = request.POST
        session_key = request.session.session_key
        user = request.user

        # Adding product to basket by product id
        product_id = data.get("product_id")
        if product_id:
            nmb = data.get("nmb") or 1
            ProductInBasket.add_product_to_basket(
                user=user,
                session_key=session_key,
                product_id=product_id,
                nmb=nmb
            )

        # Removing product from basket
        rm_product_id = data.get('remove_product_id')
        if rm_product_id:
            ProductInBasket.remove_product_from_basket(
                user=user,
                session_key=session_key,
                rm_product_id=rm_product_id
            )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        session_key = request.session.session_key
        user = request.user

        products_in_basket = ProductInBasket.get_for_user_or_session_key(
            user=user,
            session_key=session_key
        )
        products_total_price = ProductInBasket.get_basket_total_price(
            user=user,
            session_key=session_key
        )
        products_total_nmb = products_in_basket.count()

        # List of all product ids in basket. Should look like: 4,12,22 etc.
        ids_list = list(products_in_basket.values_list('product_id', flat=True))
        ids_str = ','.join([str(id) for id in ids_list])

        context = {
            'user': user,
            'products_in_basket': products_in_basket,
            'products_total_price': products_total_price,
            'products_total_nmb': products_total_nmb,
            'products_in_basket_ids': ids_str
        }

        return context


def changeProductInBasketQuantity(request):
    """
    Updates quantity of a product in basket.
    Accepts post request with product_id and qty (nmb) of product.
    """
    session_key = request.session.session_key
    user = request.user
    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")

    product = ProductInBasket.get_for_user_or_session_key(
        user=user,
        session_key=session_key,
        product_id=product_id
    ).first()

    product.nmb = int(nmb)
    product.save(force_update=True)

    return_dict = {}
    return_dict["total_product_price"] = product.total_price
    return JsonResponse(return_dict)


class CheckoutView(CreateView):
    """
    Creating order with products previously added to basket.
    Order could be assigned to authenticated user as well as to a not authenticated one.
    """

    title           = 'Order'
    model           = Order
    form_class      = OrderForm
    template_name   = 'orders/checkout.html'

    def get_initial(self):
        """
        If user has a profile with name, email etc
        it's fetched and inserted into the form as inintial data
        """
        initial = super().get_initial()

        try:
            profile = self.request.user.profile_set.get()
        except:
            return initial

        initial['customer_name']    = profile.get_full_name()
        initial['customer_phone']   = profile.phone
        initial['customer_email']   = self.request.user.email
        initial['customer_address'] = profile.address
        return initial

    def get_context_data(self, **kwargs):
        """
        Adding products in basket to template context
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        session_key = self.request.session.session_key

        products_in_basket = ProductInBasket.get_for_user_or_session_key(user=user, session_key=session_key)
        products_total_price = ProductInBasket.get_basket_total_price(user=user, session_key=session_key)
        context['products_in_basket'] = products_in_basket
        context['products_total_price'] = products_total_price
        return context

    def form_valid(self, form, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated():
            form.instance.user = self.request.user

        # Assigning a status "1" (Waiting for paimment) to order.
        form.instance.status_id = 1
        # With this line Order instance is created
        response = super().form_valid(form)
        order = self.object

        # Taking products from basket and creating a ProductInOrder objects linked to order.
        session_key = self.request.session.session_key
        products_in_basket = ProductInBasket.get_for_user_or_session_key(user=user, session_key=session_key)
        for product_in_basket in products_in_basket:
            ProductInOrder.objects.create(
                order=order,
                product=product_in_basket.product,
                nmb=product_in_basket.nmb,
                price_per_item=product_in_basket.price_per_item,
            )
            # When an order is created, products are removed from the basket
            product_in_basket.delete()

        # Sending email with order details to admins
        notify_admins_about_order(order)
        return response

    def get_success_url(self):
        return reverse('orders:success')


class SuccessView(TemplateView):
    template_name = 'orders/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user_profile_url = self.request.user.profile_set.first().get_absolute_url()
        except:
            user_profile_url = None

        context['user_profile_url'] = user_profile_url
        return context


def notify_admins_about_order(order):
    """
    The function sends email to ADMINS (specified in settings.py)
    with details about the created order.
    """
    text = f'''
{order.customer_name} made an order for {order.total_price} RUB 
Datetime: ({order.created.strftime("%Y-%m-%d %H.%M.%S")})
Phone: {order.customer_phone}
Email: {order.customer_email}
Address: {order.customer_address}
Comments: {order.comments}
Products:
'''
    for p_in_o in order.get_products_in_order():
        text += f'- {(p_in_o).product.name}, ({p_in_o.nmb})\n'

    mail_admins('Order', text)
