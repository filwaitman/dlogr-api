# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-28 23:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20161025_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='human_identifier',
            field=models.CharField(default='whatever', max_length=255),
            preserve_default=False,
        ),
    ]