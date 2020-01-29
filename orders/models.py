from django.db import models
from django.contrib.auth import get_user_model
from utils.main import disable_for_loaddata
from products.models import Product, ProductImage

User = get_user_model()


class Status(models.Model):
    """
    Status of order
    """
    name      = models.CharField(max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created   = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated   = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Order status"


class Order(models.Model):

    user            = models.ForeignKey(User, null=True, default=None)
    customer_name   = models.CharField(max_length=64, default=None)
    customer_email  = models.EmailField(blank=True, null=True, default=None)
    customer_phone  = models.CharField(max_length=48, null=True, default=None)
    customer_address = models.CharField(blank=True, null=True, max_length=128, default=None)
    comments        = models.TextField(blank=True, default=None)
    status          = models.ForeignKey(Status)
    total_price     = models.IntegerField(default=0)

    created         = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated         = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Order %s %s" % (self.id, self.status.name)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def get_products_in_order(self):
        """
        Returns products included in this order
        """
        return ProductInOrder.objects.filter(order=self)



class ProductInOrder(models.Model):

    order           = models.ForeignKey(Order, blank=True, null=True, default=None)
    product         = models.ForeignKey(Product, blank=True, null=True, default=None)
    nmb             = models.IntegerField(default=1)
    price_per_item  = models.IntegerField(default=0, verbose_name="Price")
    total_price     = models.IntegerField(default=0, verbose_name="Price")
    is_active       = models.BooleanField(default=True)
    created         = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated         = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = "Product in order"
        verbose_name_plural = "Products in order"

    def save(self, *args, **kwargs):
        self.price_per_item = self.product.price
        self.total_price = int(self.nmb) * self.product.get_price_with_discount()

        super(ProductInOrder, self).save(*args, **kwargs)



@disable_for_loaddata
def product_in_order_post_save(sender, instance, created, **kwargs):
    """
    Calculates order total price after saving (prices with discount)
    """
    order = instance.order
    all_products_in_order = ProductInOrder.objects.filter(order=order, is_active=True)
    order_total_price = all_products_in_order.aggregate(s=models.Sum('total_price'))['s']
    instance.order.total_price = order_total_price
    instance.order.save(force_update=True)

models.signals.post_save.connect(product_in_order_post_save, sender=ProductInOrder)


class ProductInBasket(models.Model):

    user            = models.ForeignKey(User, blank=True, null=True, default=None)
    session_key     = models.CharField(max_length=128, blank=True, null=True, default=True)
    order           = models.ForeignKey(Order, blank=True, null=True, default=None)
    product         = models.ForeignKey(Product, blank=True, null=True, default=None)
    nmb             = models.IntegerField(default=1)
    price_per_item  = models.IntegerField(default=0, verbose_name="Price")
    discount        = models.IntegerField(null=True, blank=True, default=0)
    total_price     = models.IntegerField(default=0, verbose_name="Price")
    is_active       = models.BooleanField(default=True)
    created         = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated         = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Product in basket"
        verbose_name_plural = "Products in basket"
        ordering = ('created',)

    def get_product_thumbnail_url(self):
        """
        URL for thumbnail of Product main image
        """
        return ProductImage.objects.get(product=self.product, is_main=True).thumbnail.url

    @staticmethod
    def add_product_to_basket(product_id, session_key=None, user=None,  nmb=1):
        """
        Adds product to a basket and assigns it to either user or, if
        user is not authenticated, to session key.
        """
        obj = get_user_or_session_key(user, session_key)
        new_product, created = ProductInBasket.objects.get_or_create(**obj,
                                                                     product_id=product_id,
                                                                     defaults={"nmb": nmb})
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    @staticmethod
    def remove_product_from_basket(rm_product_id, session_key=None, user=None):
        """
        Removes product from basket.
        """
        obj = get_user_or_session_key(user, session_key)
        ProductInBasket.objects.get(**obj, product=rm_product_id).delete()

    @staticmethod
    def get_for_user_or_session_key(session_key=None, user=None, product_id=None):
        """
        Returns queryset of products in basket for user or (if not user) session key
        """
        obj = get_user_or_session_key(user, session_key)
        products = ProductInBasket.objects.filter(**obj, is_active=True)
        if product_id:
            products.filter(product_id=product_id)
        return products

    @staticmethod
    def get_basket_total_price(session_key=None, user=None):
        """
        Returns summ of all products in basket (prices with discount)
        for particular user or session if user is not authenticated
        """
        basket_total_price = 0
        obj = get_user_or_session_key(user, session_key)
        products_in_basket = ProductInBasket.objects.filter(**obj, is_active=True)
        return products_in_basket.aggregate(s=models.Sum('total_price'))['s'] or 0

    def __str__(self):
        return "%s" % self.product.name

    def save(self, *args, **kwargs):
        self.price_per_item = self.product.price
        self.total_price = int(self.nmb) * self.product.get_price_with_discount()
        super(ProductInBasket, self).save(*args, **kwargs)


def get_user_or_session_key(user, session_key):
    """
    Returns user if user is not none and not anonymous.
    Otherwise returns session key.
    """
    if user and not user.is_anonymous():
        obj = {'user': user}
    else:
        obj = {'session_key': session_key}
    return obj
