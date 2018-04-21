from django.db import models
from django.db.models.signals import pre_save
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from rest_framework.reverse import reverse as api_reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit

from .utils import unique_slug_generator
from comments.models import Comment


class Product(models.Model):
    slug                    = models.SlugField(default=None, null=True)
    name                    = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Products")
    price                   = models.IntegerField(null=True, default=0, verbose_name="Price")
    discount                = models.IntegerField(null=True, default=0, verbose_name="Discount (percent)")
    short_description       = models.TextField(null=True, max_length=100, blank=True, default=None)
    diagonal                = models.DecimalField(null=True, max_digits=5, decimal_places=1, blank=True, default=None, verbose_name="Diagonal (inches)")
    built_in_memory         = models.IntegerField(null=True, blank=True, default=None, verbose_name="Built in memory (Gb)")
    ram                     = models.IntegerField(null=True, blank=True, default=None, verbose_name="Ram (Gb)")
    os                      = models.CharField(null=True, max_length=30, blank=True, default=None)
    screen_resolution       = models.CharField(null=True, max_length=10, blank=True, default=None)
    processor               = models.CharField(null=True, max_length=30, blank=True, default=None)
    main_camera             = models.IntegerField(null=True, blank=True, default=None, verbose_name="Main camera (Mpx)")
    other_specifications    = models.TextField(null=True, blank=True, default=None)

    is_active           = models.BooleanField(default=True)
    created             = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated             = models.DateTimeField(auto_now_add=False, auto_now=True)

    def get_main_img_url(self):
        """
        Returns main image of Product
        """
        return ProductImage.objects.get(product=self, is_main=True).image.url

    def get_price_with_discount(self):
        """
        Product price with discount (if it has discount)
        """
        discount_price = self.price - (self.price / 100 * self.discount)
        return int(discount_price)

    def __str__(self):
        return "%s, %s" % (self.price, self.name)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def get_absolute_url(self):
        return reverse("products:product", kwargs={"slug": self.slug})

    def get_api_url(self, request=None):
        return api_reverse("api:product-rud", kwargs={'pk': self.pk}, request=request)

    @property
    def comments(self):
        """
        Comments of product
        """
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        # instance.slug = create_slug(instance)
        instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_product_receiver, sender=Product)


class ProductImage(models.Model):
    image       = models.ImageField(upload_to='products_images/')
    product     = models.ForeignKey(Product, blank=True, null=True, default=None)
    is_active   = models.BooleanField(default=True)
    is_main     = models.BooleanField(default=False)
    created     = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated     = models.DateTimeField(auto_now_add=False, auto_now=True)

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




