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
                                               'A5',
                                               'A2',
                                               'Intel',
                                               'Snapdragon',
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
        self.assertTemplateUsed(response, 'home.html')

    def test_view_context(self):
        response = self.client.get(reverse('main'))

        context = {}
        for column in ['os', 'ram', 'diagonal', 'processor']:
            distinct_qs = Product.objects.all().values_list(column).distinct()
            choices = []
            for i in list(distinct_qs):
                key = column + '__' + str(i[0])
                val = i[0]
                choices.append({'key': key, 'val': val})
            context[column] = choices

        self.assertEqual(response.context['os_select'], context['os'])
        self.assertEqual(response.context['diagonal_select'], context['diagonal'])
        self.assertEqual(response.context['ram_select'], context['ram'])
        self.assertEqual(response.context['processor_select'], context['processor'])
        self.assertEqual(response.context['product_list'].count(), self.num_of_devices)


class FilteredProductsTestCase(TestCase):

    def setUp(self):
        generate_devices(self)

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/filtered_products/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('filtered_products'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('filtered_products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products_on_main_page.html')

    def test_context(self):
        response = self.client.get(reverse('filtered_products'))
        self.assertTrue('product_list' in response.context)

    def test_filter_fields(self):
        data = {
            'os__android': 0,
            'memory__max': 308,
            'memory__min': 64,
            'ram__4': 0,
            'ram__2': 0,
                }

        response = self.client.get(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertEqual(pr.os, 'android')
            self.assertNotEqual(pr.os, 'ios')
            self.assertGreaterEqual(pr.built_in_memory, data['memory__min'])
            self.assertLessEqual(pr.built_in_memory, data['memory__max'])
            self.assertIn(pr.ram, [4,2])
            self.assertNotIn(pr.ram, [3,6])

        data = {'processor__AMD': 0, 'price__max': 18000, 'price__min': 12000}
        response = self.client.get(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertEqual(pr.processor, 'AMD')
            self.assertNotEqual(pr.processor, 'A5')
            self.assertGreaterEqual(pr.price, data['price__min'])
            self.assertLessEqual(pr.price, data['price__max'])

        # Here we test multiple os and diagonal choices, when user wants to
        # see phones with different oses an diagonals
        data ={'os__android': 0, 'os__ios': 0, 'diagonal__3': 0, 'diagonal__5': 0}
        response = self.client.get(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertIn(pr.os, ['android', 'ios'])
            self.assertNotIn(pr.os, ['newos'])
            self.assertIn(pr.diagonal, [3, 5])
            self.assertNotIn(pr.diagonal, [2, 4, 6])

    def test_search(self):
        data = {'search': 'iphone'}
        response = self.client.get(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']
        for pr in product_list:
            self.assertIn('iphone', pr.name)
            self.assertNotIn('samsung', pr.name)
            self.assertNotIn('zte', pr.name)

        data = {'search': 'samsung'}
        response = self.client.get(reverse('filtered_products'), data=data)
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
        self.assertTemplateUsed(response, 'delivery.html')


class ContactsTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')

    def test_view_uses_correct_form(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].__class__, ContactForm)

    def test_send_mail(self):
        start_string = '<-------contacts EMARKET------->\n\n'
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
        self.assertTemplateUsed('orders/done.hrml')

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.to, ['m.nikolaev1@gmail.com', 'test@test.com'])
        self.assertEqual(m.subject, data['subject'])
        self.assertNotEqual(m.body, data['message'])
        self.assertEqual(m.body, start_string + data['message'])

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
