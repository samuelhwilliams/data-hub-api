# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-24 11:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170124_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskinfo',
            name='manual_rerun_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TaskInfo'),
        ),
    ]
