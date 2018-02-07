from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


from comments.models import Comment



class Product(models.Model):
    name                    = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Products")
    price                   = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Price")
    discount                = models.IntegerField(null=True, blank=True, default=0, verbose_name="Discount (percent)")
    short_description       = models.TextField(max_length=100, blank=True, null=True, default=None)
    diagonal                = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, default=None, verbose_name="Diagonal (inches)")
    built_in_memory         = models.IntegerField(null=True, blank=True, default=None, verbose_name="Built in memory (Gb)")
    ram                     = models.IntegerField(null=True, blank=True, default=None, verbose_name="Ram (Gb)")
    os                      = models.CharField(max_length=30, blank=True, null=True, default=None)
    screen_resolution       = models.CharField(max_length=10, blank=True, null=True, default=None)
    processor               = models.CharField(max_length=30, blank=True, null=True, default=None)
    main_camera             = models.IntegerField(null=True, blank=True, default=None, verbose_name="Main camera (Mpx)")
    other_specifications    = models.TextField(blank=True, null=True, default=None)

    is_active           = models.BooleanField(default=True)
    created             = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated             = models.DateTimeField(auto_now_add=False, auto_now=True)

    def get_main_img_url(self):
        return ProductImage.objects.get(product=self, is_main=True).image.url

    def get_price_with_discount(self):
        return self.price - (self.price / 100 * self.discount)

    def __str__(self):
        return "%s, %s" % (self.price, self.name)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def get_absolute_url(self):
        return reverse("product", kwargs={"product_id": self.id})


    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type



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



