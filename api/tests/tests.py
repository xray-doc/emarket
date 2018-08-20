from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse as api_reverse

from products.models import Product


payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler  = api_settings.JWT_ENCODE_HANDLER
User = get_user_model()



class ProductAPITestCase(APITestCase):
    def setUp(self):
        user_obj = User(username='testuser', email='test@test.com')
        user_obj.set_password("somepass")
        user_obj.save()
        product = Product.objects.create(
                name='ZTE',
                price=22000
                )

    def test_single_user(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_single_post(self):
        post_count = Product.objects.count()
        self.assertEqual(post_count, 1)

    def test_user_is_staff(self):
        user = User.objects.first()
        self.assertFalse(user.is_staff)

    def test_get_product_list_and_product_rud(self):
        data = {}
        url = api_reverse("api:products-list")
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = api_reverse("api:product-rud", kwargs=({'pk':1}))
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_list_with_query(self):
        product2 = Product.objects.create(
            name='Iphone X',
        )

        # without query at first
        data = {}
        url = api_reverse("api:products-list")
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # with query - seaching iphones
        data = {'q': 'iphone'}
        url = api_reverse("api:products-list")
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Iphone X')

    def test_update_product(self):
        product = Product.objects.first()
        url = product.get_api_url()
        data = {"name": "Huawei", "price": 22000}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_with_user(self):
        product = Product.objects.first()
        url = product.get_api_url()
        data = {"name": "Huawei", "price": 22000}

        user_obj = User.objects.first()

        payload = payload_handler(user_obj)
        token_rsp = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_rsp)  # JWT <token>
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) # Because is_staff == False

    def test_update_product_with_staff_user(self):
        product = Product.objects.first()
        url = product.get_api_url()
        data = {"name": "Huawei", 'price': 22000}

        staff_user = User(username='staffuser', email='staff_user@test.com')
        staff_user.set_password("somestaffpass")
        staff_user.is_staff = True
        staff_user.save()

        payload = payload_handler(staff_user)
        token_rsp = encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_rsp)  # JWT <token>
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)