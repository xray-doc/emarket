from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


# class Operational_system(models.Model):
#     name = models.CharField(max_length=64, blank=True, null=True, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "OS"
#         verbose_name_plural = "OS"
#
# class Diagonal(models.Model):
#     name = models.DecimalField(max_digits=2, decimal_places=1, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "Diagonal"
#         verbose_name_plural = "Diagonals"
#
# class ScreenResolution(models.Model):
#     name = models.CharField(max_length=10, blank=True, null=True, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "Screen resolution"
#         verbose_name_plural = "Screen resolutions"
#
# class BuiltInMemory(models.Model):
#     name = models.IntegerField(null=True, blank=True, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "Built in memory"
#         verbose_name_plural = "Built in memory"
#
# class Ram(models.Model):
#     name = models.IntegerField(null=True, blank=True, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "RAM"
#         verbose_name_plural = "RAM"
#
# class Processor(models.Model):
#     name = models.CharField(max_length=40, blank=True, null=True, default=None)
#     is_active = models.BooleanField(default=True)
#
#     created = models.DateTimeField(auto_now_add=True, auto_now=False)
#     updated = models.DateTimeField(auto_now_add=False, auto_now=True)
#
#     def __str__(self):
#         return "%s" % self.name
#
#     class Meta:
#         verbose_name = "Processor"
#         verbose_name_plural = "Processors"


class Product(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Price")
    discount = models.IntegerField(null=True, blank=True, default=0)
    short_description = models.TextField(max_length=100, blank=True, null=True, default=None)

    diagonal = models.IntegerField(null=True, blank=True, default=None)
    built_in_memory = models.IntegerField(null=True, blank=True, default=None)
    ram = models.IntegerField(null=True, blank=True, default=None)
    os = models.CharField(max_length=30, blank=True, null=True, default=None)
    screen_resolution = models.CharField(max_length=10, blank=True, null=True, default=None)
    processor = models.CharField(max_length=30, blank=True, null=True, default=None)

    description = models.TextField(blank=True, null=True, default=None)
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
                                    processors=[ResizeToFit(200, 100)],
                                    format='JPEG',
                                    options={'quality': 60})
    else:
        thumbnail = None


    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"



