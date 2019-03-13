# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-28 20:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0004_auto_20170925_0720'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ngram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('word', models.CharField(max_length=255, null=True, verbose_name='Word')),
                ('impressions', models.DecimalField(db_index=True, decimal_places=6, max_digits=18, null=True, verbose_name='Impressions')),
                ('clicks', models.DecimalField(db_index=True, decimal_places=6, max_digits=18, null=True, verbose_name='Clicks')),
                ('cost', models.DecimalField(db_index=True, decimal_places=6, max_digits=18, null=True, verbose_name='Cost')),
                ('conversions', models.DecimalField(db_index=True, decimal_places=6, max_digits=18, null=True, verbose_name='Conversions')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ngrams', to='clients.Client')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]