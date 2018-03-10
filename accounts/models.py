from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.ForeignKey(User)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default=None)
    first_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    second_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    phone = models.CharField(blank=True, null=True, default=None, max_length=48)
    address = models.CharField(blank=True, null=True, default=None, max_length=128)
    #TODO: gender choices
