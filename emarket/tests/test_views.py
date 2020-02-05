from django.core import mail
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
import random

from products.models import Product
from ..forms import ContactForm


def generate_devices(self):
    """
    Creates products for test database. Some parametes of a product
    are faked and some randomly choiced from a list.
    """
    self.num_of_devices = 70
    fields = [                    # These fields we want to be FAKED by mixer
        'short_description',
        'screen_resolution',
        'main_camera',
        'other_specifications',
    ]

    kwargs = {field: mixer.FAKE for field in fields}
    mixer.cycle(self.num_of_devices).blend(Product,
                                           name=lambda: random.choice([
                                              'apple iphone',
                                               'iphone',
                                              'samsung',
                                              'samsung note'
                                              'huawei',
                                              'oneplus',
                                              'zte'
                                           ]),
                                           processor=lambda: random.choice([
                                               'A8',
                                               'A9',
                                               'Qualcomm 1400 Mgz',
                                               'A10X',
                                               'AMD'
                                           ]),
                                           os=lambda: random.choice(['ios', 'android', 'newos']),
                                           ram=lambda: random.choice([2, 3, 4, 6]),
                                           price=lambda: random.randrange(5000, 30000),
                                           diagonal=lambda: random.randint(3, 6),
                                           discount=lambda: random.randint(0, 100),
                                           built_in_memory=lambda: random.randrange(16, 400, 4),
                                           **kwargs
                                           )


class MainTestCase(TestCase):

    def setUp(self):
        generate_devices(self)

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/main/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main'))

        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emarket/home.html')


class FilteredProductsTestCase(TestCase):

    def setUp(self):
        generate_devices(self)

    def test_view_url_exists_and_accessible(self):
        response = self.client.post('/filtered_products/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('filtered_products'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.post(reverse('filtered_products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emarket/products_on_main_page.html')

    def test_context(self):
        response = self.client.post(reverse('filtered_products'))
        self.assertTrue('product_list' in response.context)

    def test_filter_fields(self):
        data = {
            'os': 'android',
            'memory_max': 100,
            'memory_min': 20,
            'ram': [2,4]
        }

        response = self.client.post(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertEqual(pr.os, 'android')
            self.assertNotEqual(pr.os, 'ios')
            self.assertGreaterEqual(pr.built_in_memory, data['memory_min'])
            self.assertLessEqual(pr.built_in_memory, data['memory_max'])
            self.assertIn(pr.ram, [4,2])
            self.assertNotIn(pr.ram, [3,6])

        data = {
            'processor': 'Qualcomm 1400 Mgz',
            'max_price': 18000,
            'min_price': 12000
        }
        response = self.client.post(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertEqual(pr.processor, 'Qualcomm 1400 Mgz')
            self.assertNotEqual(pr.processor, 'A5')
            self.assertGreaterEqual(pr.price, data['min_price'])
            self.assertLessEqual(pr.price, data['max_price'])

        # Here we test multiple os and diagonal choices, when user wants to
        # see phones with different oses an diagonals
        data ={
            'os': ['android', 'newos'],
            'diagonal': [5.0, 6.0],
            'processor': 'AMD'
        }
        response = self.client.post(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']

        for pr in product_list:
            self.assertIn(pr.os, ['android', 'newos'])
            self.assertNotIn(pr.os, ['ios'])
            self.assertIn(pr.diagonal, [5, 6])
            self.assertNotIn(pr.diagonal, [2, 4, 3])
            self.assertEqual(pr.processor, 'AMD')

    def test_search(self):
        data = {'search': 'iphone'}
        response = self.client.post(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertIn('iphone', pr.name)
            self.assertNotIn('samsung', pr.name)
            self.assertNotIn('zte', pr.name)

        data = {'search': 'samsung'}
        response = self.client.post(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertIn('samsung', pr.name)
            self.assertNotIn('iphone', pr.name)
            self.assertNotIn('zte', pr.name)


class DeliveryTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/delivery/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('delivery'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('delivery'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emarket/delivery.html')


class ContactsTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emarket/contacts.html')

    def test_view_uses_correct_form(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].__class__, ContactForm)

    def test_send_mail(self):
        data = {
            'subject': 'Hello emarket',
            'sender': 'test@test.com',
            'message': 'I am testuser',
            'copy': True
        }

        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(reverse('contacts'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('success'))

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.to, ['m.nikolaev1@gmail.com', 'test@test.com'])
        self.assertIn(data['subject'], m.subject)
        self.assertIn(data['message'], m.body)
        self.assertIn(data['sender'], m.body)

    def test_send_mail_without_copy(self):
        data = {
            'subject': 'Hello emarket',
            'sender': 'test@test.com',
            'message': 'I am testuser',
            'copy': False
        }

        response = self.client.post(reverse('contacts'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('success'))
        m = mail.outbox[0]
        self.assertEqual(m.to, ['m.nikolaev1@gmail.com'])
