# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-25 06:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='client',
            name='failed_tries',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='used to notify on fails', null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_budget_adwords',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Spend (AdWords)'),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_budget_bingads',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Spend (BingAds)'),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_budget_facebookads',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Spend (FacebookAds)'),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_conversions_adwords',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Conversion (AdWords)'),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_conversions_bingads',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Conversion (BingAds)'),
        ),
        migrations.AddField(
            model_name='client',
            name='planned_conversions_facebookads',
            field=models.DecimalField(decimal_places=2, max_digits=16, null=True, verbose_name='Goal for Conversion (FacebookAds)'),
        ),
        migrations.AlterField(
            model_name='client',
            name='adwords_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='AdWords ID'),
        ),
        migrations.AlterField(
            model_name='client',
            name='bingads_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='BingAds ID'),
        ),
        migrations.AlterField(
            model_name='client',
            name='facebookads_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Facebook Ads ID'),
        ),
    ]
