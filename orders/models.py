from django.db import models
from products.models import Product
from django.db.models.signals import post_save
from django.contrib.auth.models import User


class Status(models.Model):
    name = models.CharField("Название", max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField("Активен", default=True)

    created = models.DateTimeField("Создан", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлен", auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы заказа"




class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None, verbose_name="Пользователь")
    customer_name = models.CharField("Имя", max_length=64, blank=True, null=True, default=None)
    customer_email = models.EmailField("Email", blank=True, null=True, default=None)
    customer_phone = models.CharField("Телефон", blank=True, null=True, default=None, max_length=48)
    customer_address = models.CharField("Адрес", blank=True, null=True, default=None, max_length=128)
    comments = models.TextField("Комментарий", blank=True, null=True, default=None)
    status = models.ForeignKey(Status, verbose_name="Статус")
    total_price = models.DecimalField("Сумма заказа", max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField("Создан", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлен", auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Заказ %s %s" % (self.id, self.status.name)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"



class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, verbose_name="Заказ", blank=True, null=True, default=None)
    product = models.ForeignKey(Product, verbose_name="Товар", blank=True, null=True, default=None)
    nmb = models.IntegerField("Количество", default=1)
    price_per_item = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField("Общая цена", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Активен", default=True)
    created = models.DateTimeField("Создан", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлен", auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"


    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        discount = self.product.discount
        self.price_per_item = price_per_item
        price_per_item -= price_per_item / 100 * discount
        self.total_price = int(self.nmb) * price_per_item

        super(ProductInOrder, self).save(*args, **kwargs)




def product_in_order_post_save(sender, instance, created, **kwargs):
    order = instance.order
    all_products_in_order = ProductInOrder.objects.filter(order=order, is_active=True)

    order_total_price = 0
    for item in all_products_in_order:
        order_total_price += item.total_price

    instance.order.total_price = order_total_price
    instance.order.save(force_update=True)



post_save.connect(product_in_order_post_save, sender=ProductInOrder)




class ProductInBasket(models.Model):
    session_key = models.CharField("Ключ сессии", max_length=128, blank=True, null=True, default=True)
    order = models.ForeignKey(Order, verbose_name="Заказ", blank=True, null=True, default=None)
    product = models.ForeignKey(Product, verbose_name="Товар", blank=True, null=True, default=None)
    nmb = models.IntegerField("Количество", default=1)
    price_per_item = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2, default=0)
    discount = models.IntegerField("Скидка", null=True, blank=True, default=0)
    total_price = models.DecimalField("Общая цена", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Активен", default=True)
    created = models.DateTimeField("Создан", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлен", auto_now_add=False, auto_now=True)

    def get_basket_total_price(session_key):
        basket_total_price = 0
        products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)
        for product in products_in_basket:
            basket_total_price += product.total_price
        return basket_total_price

    def __str__(self):
        return "%s" % self.product.name

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        discount = self.product.discount
        self.price_per_item = price_per_item
        price_per_item -= price_per_item / 100 * discount
        self.total_price = int(self.nmb) * price_per_item

        super(ProductInBasket, self).save(*args, **kwargs)