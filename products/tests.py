from django.test import TestCase

from .models import Product


class ProductTestCase(TestCase):
    
    def test_get_price_with_discount(self):
    	product = Product.objects.create(
    		price=10000,
    		discount=10
    		)
    	product.save()
    	discounted_price = int(product.get_price_with_discount())
    	self.assertEqual(discounted_price, 9000)

    	product = Product.objects.create(
    		price=25000,
    		discount=8
    		)
    	product.save()
    	discounted_price = int(product.get_price_with_discount())
    	self.assertEqual(discounted_price, 23000)

    def test___str__(self):
    	product = Product.objects.create(
    		price=25000,
    		name='meizu mx5'
    		)
    	product.save()
    	self.assertEqual(str(product), '25000, meizu mx5')