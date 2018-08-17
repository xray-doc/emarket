import os
from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Product, ProductImage


class ProductTestCase(TestCase):

    def setUp(self):
        product = mixer.blend(Product, price=10000, discount=10, name='Samsung')
        product.save()

    def tearDown(self):
        for pi in ProductImage.objects.all():
            url = os.getcwd() + pi.image.url
            os.remove(url)

    def test_get_price_with_discount(self):
        product = mixer.blend(Product, price=10000, discount=10)
        product.save()
        discounted_price = int(product.get_price_with_discount())
        self.assertEqual(discounted_price, 9000)

        product = mixer.blend(Product, price=25000, discount=8)
        product.save()
        discounted_price = int(product.get_price_with_discount())
        self.assertEqual(discounted_price, 23000)

    def test___str__(self):
        product = mixer.blend(Product, price=25000, name='meizu mx5')
        product.save()
        self.assertEqual(str(product), '25000, meizu mx5')

    def test_get_main_image_url(self):
        product = Product.objects.first()
        image_main = mixer.blend(ProductImage, product=product, is_main=True)
        image_not_main = mixer.blend(ProductImage, product=product, is_main=False)

        self.assertEqual(
            product.get_main_img_url(),
            image_main.image.url
        )
        self.assertNotEqual(
            product.get_main_img_url(),
            image_not_main.image.url
        )

    def test_get_absolute_url(self):
        absolute_url = '/products/iphonex/'

        product = mixer.blend(Product, name='IPhoneX')
        url = product.get_absolute_url()
        self.assertEqual(url, absolute_url)

        product2 = mixer.blend(Product, name='IPhoneX')
        url2 = product2.get_absolute_url()
        self.assertNotEqual(url2, absolute_url)
        self.assertTrue(url2.find(absolute_url[:1]) != -1)


class ProductImageTestCase(TestCase):

    def test___str__(self):
        image_not_main = ProductImage.objects.create(is_main=False)
        id = image_not_main.id
        self.assertEqual(str(id), str(image_not_main))




