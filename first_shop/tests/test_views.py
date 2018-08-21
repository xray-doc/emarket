from django.core import mail
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from products.models import Product
from ..forms import ContactForm

class MainTestCase(TestCase):

    def setUp(self):
        self.num_of_devices = 5
        fields = [                   # These fields we want to be FAKED
            'name',                  # by mixer
            'price',
            'discount',
            'short_description',
            'diagonal',
            'built_in_memory',
            'ram',
            'os',
            'screen_resolution',
            'processor',
            'main_camera',
            'other_specifications',
        ]

        kwargs = {field: mixer.FAKE for field in fields}
        mixer.cycle(self.num_of_devices).blend(Product, **kwargs)

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
        self.num_of_devices = 10
        fields = [                   # These fields we want to be FAKED
            'name',                  # by mixer
            'price',
            'discount',
            'short_description',
            'diagonal',
            'built_in_memory',
            'ram',
            'os',
            'screen_resolution',
            'processor',
            'main_camera',
            'other_specifications',
        ]

        kwargs = {field: mixer.FAKE for field in fields}
        mixer.cycle(self.num_of_devices).blend(Product, **kwargs)

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

    def test_filter(self):
        self.assertTrue('it is too hard to test this filter thoroughly')

        data = {
            'memory__max': 5555,
            'memory__min': 2700,
        }
        response = self.client.get(reverse('filtered_products'), data=data)
        product_list = response.context['product_list']

        for product in product_list:
            memory = product.built_in_memory
            self.assertGreaterEqual(memory, data['memory__min'])
            self.assertLessEqual(memory, data['memory__max'])


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
        self.assertRedirects(response, reverse('main'))
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
        self.assertRedirects(response, reverse('main'))
        m = mail.outbox[0]
        self.assertEqual(m.to, ['m.nikolaev1@gmail.com'])
