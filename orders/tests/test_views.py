from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from mixer.backend.django import mixer
import json

from ..models import Order, Status, ProductInOrder, ProductInBasket
from products.models import Product

User = get_user_model()


class UpdateBasketListViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='somep')
        self.user2 = User.objects.create_user(username='testuser2', password='somep')

        self.pr1 = mixer.blend(Product, price=12000)
        self.pr2 = mixer.blend(Product, price=13300)
        self.pr3 = mixer.blend(Product, price=14600)

        # self.order1 = mixer.blend(Order, user=self.user1)
        # self.order2 = mixer.blend(Order, user=self.user2)

        self.pr_in_basket1 = mixer.blend(
            ProductInBasket,
            user = self.user1,
            product = self.pr1,
            # order = self.order1
        )
        self.pr_in_basket2 = mixer.blend(
            ProductInBasket,
            user=self.user1,
            product=self.pr2,
        )
        self.pr_in_basket3 = mixer.blend(
            ProductInBasket,
            user=self.user2,
            product=self.pr2,
        )

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/orders/update_basket_list/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'basket_items_list.html')

    def test_view_context_keys(self):
        response = self.client.get(reverse('orders:basket_list'))
        expected_context_keys = [
            'products_total_nmb',
            'products_in_basket_ids',
            'products_in_basket',
            'products_total_price'
        ]

        for key in expected_context_keys:
            self.assertIn(key, response.context)

    def test_view_context_with_user(self):

        # ::::First user::::
        self.client.login(username='testuser1', password='somep')

        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products_total_nmb'], 2)

        ids = str(self.pr_in_basket1.product.id) + ',' + str(self.pr_in_basket2.product.id) + ','
        self.assertEqual(response.context['products_in_basket_ids'], ids)

        total_price = self.pr_in_basket1.total_price + self.pr_in_basket2.total_price
        self.assertEqual(response.context['products_total_price'], total_price)

        # ::::And logout::::
        self.client.logout()
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.context['products_total_nmb'], 0)
        self.assertEqual(response.context['products_in_basket_ids'], '')
        self.assertEqual(response.context['products_total_price'], 0)

        # ::::And another user::::
        self.client.login(username='testuser2', password='somep')
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.context['products_total_nmb'], 1)

        ids = str(self.pr_in_basket3.product.id) + ','
        self.assertEqual(response.context['products_in_basket_ids'], ids)

        total_price = self.pr_in_basket3.total_price
        self.assertEqual(response.context['products_total_price'], total_price)

    def test_add_product_to_basket(self):
        self.client.login(username='testuser1', password='somep')
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)

        pr_id = self.pr3.id
        response= self.client.post(reverse('orders:basket_list'), data={'product_id': pr_id, 'nmb': 3})
        self.assertEqual(response.context['products_total_nmb'], 3)

        ids = str(self.pr_in_basket1.product.id) + ',' + str(self.pr_in_basket2.product.id) + ','
        ids += str(pr_id) + ','
        self.assertEqual(response.context['products_in_basket_ids'], ids)

        total_price = self.pr_in_basket1.total_price \
                      + self.pr_in_basket2.total_price \
                      + self.pr3.price * 3
        self.assertEqual(response.context['products_total_price'], total_price)

    def test_delete_product_from_basket(self):
        self.client.login(username='testuser1', password='somep')
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)

        pr_id = self.pr_in_basket1.id
        response = self.client.get(reverse('orders:basket_list'), data={'remove_product_id': pr_id})
        self.assertEqual(response.context['products_total_nmb'], 1)

        ids = str(self.pr_in_basket2.product.id) + ','
        self.assertEqual(response.context['products_in_basket_ids'], ids)

    def test_view_without_user(self):
        response = self.client.get(reverse('orders:basket_list'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['products_total_nmb'], 0)
        self.assertEqual(response.context['products_in_basket_ids'], '')
        self.assertEqual(response.context['products_total_price'], 0)

        pr3_id = self.pr3.id
        response = self.client.post(reverse('orders:basket_list'), data={'product_id': pr3_id, 'nmb': 2})
        self.assertEqual(response.context['products_total_nmb'], 1)
        self.assertEqual(response.context['products_in_basket_ids'], str(pr3_id) + ',')
        self.assertEqual(response.context['products_total_price'], self.pr3.price * 2)

        pr1_id = self.pr1.id
        response = self.client.post(reverse('orders:basket_list'), data={'product_id': pr1_id, 'nmb': 1})
        self.assertEqual(response.context['products_total_nmb'], 2)
        ids = str(pr3_id) + ',' + str(pr1_id) + ','
        self.assertEqual(response.context['products_in_basket_ids'], ids)
        price = self.pr3.price * 2 + self.pr1.price
        self.assertEqual(response.context['products_total_price'], price)


class ChangeProductInBasketViewTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='somep')
        self.pr1 = mixer.blend(Product, price=12000)
        self.pr_in_basket1 = mixer.blend(
            ProductInBasket,
            user = self.user1,
            product = self.pr1,
        )

    def test_change_product_in_basket_nmb(self):
        data = {'product_id': self.pr1.id, 'nmb': 11}

        self.client.login(username='testuser1', password='somep')
        response = self.client.post(reverse('orders:changeProduct'), data=data)

        resp = json.loads(response.content)
        self.assertTrue('total_product_price' in resp)
        self.assertEqual(resp['total_product_price'], self.pr1.price * 11)


class CheckoutViewTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')

    def test_view_context_keys(self):
        response = self.client.get(reverse('orders:checkout'))