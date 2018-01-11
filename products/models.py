from django.db import models



class Operational_system(models.Model):
    name = models.CharField("Название", max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField("Активна", default=True)

    created = models.DateTimeField("Создана", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлена", auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = "ОС"
        verbose_name_plural = "ОС"



class Product(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена")
    os = models.ForeignKey(Operational_system, verbose_name='ОС')
    short_description = models.CharField("Краткое описание", max_length=100, blank=True, null=True, default=None)
    description = models.TextField("Описание", blank=True, null=True, default=None)
    discount = models.IntegerField("Скидка", null=True, blank=True, default=0)

    is_active = models.BooleanField("Активен", default=True)
    created = models.DateTimeField("Создан", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлен", auto_now_add=False, auto_now=True)

    def get_main_img_url(self):
        return ProductImage.objects.get(product=self, is_main=True).image.url

    def __str__(self):
        return "%s, %s" % (self.price, self.name)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"



class ProductImage(models.Model):
    image = models.ImageField("Изображение", upload_to='products_images/')
    product = models.ForeignKey(Product, verbose_name="Товар", blank=True, null=True, default=None)
    is_active = models.BooleanField("Активно", default=True)
    is_main = models.BooleanField("Главное", default=False)
    created = models.DateTimeField("Создано", auto_now_add=True, auto_now=False)
    updated = models.DateTimeField("Обновлено", auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
