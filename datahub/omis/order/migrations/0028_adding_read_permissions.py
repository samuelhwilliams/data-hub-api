# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 12:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0027_hourlyrate_disabled_on'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': (('read_order', 'Can read order'),)},
        ),
    ]
