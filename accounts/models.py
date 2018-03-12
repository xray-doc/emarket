from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class Profile(models.Model):
    user = models.ForeignKey(User)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default=None) #TODO: eclude
    first_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    second_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField(blank=True, null=True, default=None)
    phone = models.CharField(blank=True, null=True, default=None, max_length=48)
    address = models.CharField(blank=True, null=True, default=None, max_length=128)

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.second_name)

    def __str__(self):
        return "%s profile" % self.user.username