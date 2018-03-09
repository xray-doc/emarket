from django.db import models
from products.models import Product
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from utils.main import disable_for_loaddata
from products.models import *

User = get_user_model()


class Status(models.Model):
    """
    Status of order
    """
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Order status"


class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    customer_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    customer_email = models.EmailField(blank=True, null=True, default=None)
    customer_phone = models.CharField(blank=True, null=True, default=None, max_length=48)
    customer_address = models.CharField(blank=True, null=True, default=None, max_length=128)
    comments = models.TextField(blank=True, null=True, default=None)
    status = models.ForeignKey(Status)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Order %s %s" % (self.id, self.status.name)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"



class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None)
    product = models.ForeignKey(Product, blank=True, null=True, default=None)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

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

    order_total_price = 0
    for item in all_products_in_order:
        order_total_price += item.total_price

    instance.order.total_price = order_total_price
    instance.order.save(force_update=True)



post_save.connect(product_in_order_post_save, sender=ProductInOrder)



class ProductInBasket(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None)
    session_key = models.CharField(max_length=128, blank=True, null=True, default=True)
    order = models.ForeignKey(Order, blank=True, null=True, default=None)
    product = models.ForeignKey(Product, blank=True, null=True, default=None)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.IntegerField(null=True, blank=True, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def get_basket_total_price(session_key=None, user=None):
        """
        Returns summ of all products in basket (prices with discount)
        for particular user or session if user is not authenticated
        """
        basket_total_price = 0
        if user:
            products_in_basket = ProductInBasket.objects.filter(user=user, is_active=True)
        else:
            products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)

        for product in products_in_basket:
            basket_total_price += product.total_price
        return basket_total_price

    def get_product_thumbnail_url(self):
        """
        URL for thumbnail of Product main image
        """
        return ProductImage.objects.get(product=self.product, is_main=True).thumbnail.url

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = "Product in basket"
        verbose_name_plural = "Products in basket"
        ordering = ('created',)

    def save(self, *args, **kwargs):
        self.price_per_item = self.product.price
        self.total_price = int(self.nmb) * self.product.get_price_with_discount()

        super(ProductInBasket, self).save(*args, **kwargs)