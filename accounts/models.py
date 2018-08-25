from django.db import models
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

User = get_user_model()

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class Profile(models.Model):
    user = models.ForeignKey(User)
    first_name = models.CharField(max_length=64, null=True, default=None)
    second_name = models.CharField(max_length=64, null=True, default=None)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='M')
    birth_date = models.DateField(blank=True, null=True, default=None)
    phone = models.CharField(blank=True, null=True, default=None, max_length=48)
    address = models.CharField(blank=True, null=True, default=None, max_length=128)

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.second_name)

    def get_absolute_url(self):
        return reverse("accounts:profile", kwargs={"username": self.user.username})

    def __str__(self):
        return "%s profile" % self.user.username