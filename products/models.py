from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class Operational_system(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "OS"
        verbose_name_plural = "OS"



class Product(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Price")
    os = models.ForeignKey(Operational_system, verbose_name='OS')
    short_description = models.CharField(max_length=100, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    discount = models.IntegerField(null=True, blank=True, default=0)

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def get_main_img_url(self):
        return ProductImage.objects.get(product=self, is_main=True).image.url

    def get_price_with_discount(self):
        return self.price - (self.price / 100 * self.discount)

    def __str__(self):
        return "%s, %s" % (self.price, self.name)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"



class ProductImage(models.Model):
    image = models.ImageField(upload_to='products_images/')
    product = models.ForeignKey(Product, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    if is_main:
        thumbnail = ImageSpecField(source='image',
                                    processors=[ResizeToFit(100, 50)],
                                    format='JPEG',
                                    options={'quality': 60})
    else:
        thumbnail = None


    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"



