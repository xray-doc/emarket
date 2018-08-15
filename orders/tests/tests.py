from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Order, Status, ProductInOrder
from products.models import Product

class OrderTestCase(TestCase):

    def setUp(self):
        status = mixer.blend(Status, name='checking')
        order = mixer.blend(Order, status=status)
        product = mixer.blend(Product, price=10000)

    def test_status_str(self):
        status = Status.objects.first()
        status_str = str(status)
        self.assertEqual(status_str, 'checking')

    def test_order_str(self):
        order = Order.objects.first()
        id = order.id
        order_str = str(order)
        self.assertEqual(order_str, f'Order {id} checking')

    def test_get_products_in_order(self):
        order = Order.objects.first()
        product = Product.objects.first()
        p_in_order_1 = mixer.blend(ProductInOrder, order=order, product=product)
        p_in_order_2 = mixer.blend(ProductInOrder, order=order, product=product)

        products_in_order = order.get_products_in_order()

        self.assertEqual(products_in_order.count(), 2)
