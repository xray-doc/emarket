from django.test import TestCase
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer

from ..models import Order, Status, ProductInOrder, ProductInBasket
from products.models import Product

User = get_user_model()


class OrderTestCase(TestCase):

    def setUp(self):
        status = mixer.blend(Status, name='checking')
        order = mixer.blend(Order, customer_name='Derek', comments='Ok', status=status)
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
        self.assertEqual(order.get_products_in_order().count(), 2)

        ids1 = order.get_products_in_order().values_list('id', flat=True).order_by('id')
        ids2 = ProductInOrder.objects.values_list('id', flat=True).order_by('id')
        self.assertEqual(list(ids1), list(ids2))


class ProductInOrderTestCase(TestCase):

    def test_product_in_order___str__(self):
        product = mixer.blend(Product, name='Nokia')
        pr_in_order = ProductInOrder(product=product)
        self.assertEqual(str(pr_in_order), 'Nokia')

    def test_product_in_order_save(self):
        order = mixer.blend(Order, customer_name='Derek', comments='Ok')
        product_without_discount = mixer.blend(Product, price=12000)
        pr_in_order = mixer.blend(ProductInOrder, product=product_without_discount, order=order, nmb=3)
        estimated_price = 12000 * 3
        self.assertEqual(pr_in_order.total_price, estimated_price)

        product_with_discount = mixer.blend(Product, price=9000, discount=30)
        pr_in_order2 = mixer.blend(ProductInOrder, product=product_with_discount, order=order, nmb=2)
        estimated_price2 = 6300 * 2
        self.assertEqual(pr_in_order2.total_price, estimated_price2)

        self.assertEqual(order.total_price, estimated_price + estimated_price2)


class ProductInBasketTestCase(TestCase):

    def setUp(self):
        self.prod1 = mixer.blend(Product, price=12500)
        self.prod2 = mixer.blend(Product, price=8500)
        self.prod3 = mixer.blend(Product, price=12000, discount=12)

    def test_get_for_user_or_session_key(self):
        user1 = mixer.blend(User)
        user2 = mixer.blend(User)
        session_key = 'asdfsljkljlk2j34234012'

        prod_in_basket1 = mixer.blend(ProductInBasket, user=user1, product=self.prod1)
        prod_in_basket2 = mixer.blend(ProductInBasket, user=user1, product=self.prod2)
        prod_in_basket3 = mixer.blend(ProductInBasket, user=user2, product=self.prod3)
        prod_in_basket4 = mixer.blend(ProductInBasket, user=user2, product=self.prod2)
        prod_in_basket5 = mixer.blend(ProductInBasket, session_key=session_key, product=self.prod1)

        result = ProductInBasket.get_for_user_or_session_key(user=user1, product_id=self.prod1.id)
        self.assertEqual(prod_in_basket1, result.first())
        result = ProductInBasket.get_for_user_or_session_key(user=user1, product_id=self.prod2.id)
        self.assertEqual(prod_in_basket2, result.first())
        self.assertNotEqual(prod_in_basket1, result.first())

        result = ProductInBasket.get_for_user_or_session_key(user=user2, product_id=self.prod3.id)
        self.assertEqual(prod_in_basket3, result.first())
        result = ProductInBasket.get_for_user_or_session_key(user=user2, product_id=self.prod2.id)
        self.assertEqual(prod_in_basket4, result.first())

        result = ProductInBasket.get_for_user_or_session_key(session_key=session_key, product_id=self.prod1.id)
        self.assertEqual(prod_in_basket5, result.first())

    def test_get_busket_total_price_with_user(self):
        user = mixer.blend(User)

        prod_in_basket1 = mixer.blend(ProductInBasket, user=user, product=self.prod1)
        prod_in_basket2 = mixer.blend(ProductInBasket, user=user, product=self.prod2)
        self.assertEqual(ProductInBasket.get_basket_total_price(user=user), 21000)

        prod_in_basket3 = mixer.blend(ProductInBasket, user=user, product=self.prod3)
        self.assertEqual(ProductInBasket.get_basket_total_price(user=user), 31560,
                         msg='Should substract discount when counting total price')

    def test_get_busket_total_price_with_session_key(self):
        session_key = 2123141241

        prod_in_basket2 = mixer.blend(ProductInBasket, session_key=session_key, product=self.prod2)
        prod_in_basket1 = mixer.blend(ProductInBasket, session_key=session_key, product=self.prod1)
        self.assertEqual(ProductInBasket.get_basket_total_price(session_key=session_key), 21000)

        prod_in_basket3 = mixer.blend(ProductInBasket, session_key=session_key, product=self.prod3)
        self.assertEqual(ProductInBasket.get_basket_total_price(session_key=session_key), 31560,
                         msg='Should substract discount when counting total price')

    def test_product_in_basket___str__(self):
        prod = mixer.blend(Product, name='SmartphoneXXX')
        prod_in_basket = mixer.blend(ProductInBasket, product=prod)
        self.assertEqual(str(prod_in_basket), 'SmartphoneXXX')

    def test_save(self):
        prod_in_basket = mixer.blend(ProductInBasket, product=self.prod1)
        self.assertEqual(prod_in_basket.price_per_item, self.prod1.price)

        prod_in_basket = mixer.blend(ProductInBasket, product=self.prod3, nmb=4)
        self.assertEqual(prod_in_basket.total_price, 10560*4,
                         msg='Total price should consider discount')


