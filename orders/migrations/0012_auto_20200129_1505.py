# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-29 15:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20180314_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comments',
            field=models.TextField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_name',
            field=models.CharField(default=None, max_length=64),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_phone',
            field=models.CharField(default=None, max_length=48, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]