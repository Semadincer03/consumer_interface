# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 13:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Destination',
        ),
        migrations.DeleteModel(
            name='Hotel',
        ),
    ]
