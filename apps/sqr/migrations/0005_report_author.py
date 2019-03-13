# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-27 12:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sqr', '0004_auto_20170926_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]