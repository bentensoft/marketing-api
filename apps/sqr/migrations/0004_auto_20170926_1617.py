# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-26 16:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sqr', '0003_report_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'Active'), ('added', 'Added'), ('excluded', 'Excluded')], default='active', max_length=16, null=True),
        ),
    ]
