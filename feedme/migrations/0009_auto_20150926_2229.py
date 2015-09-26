# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0008_auto_20150428_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='price',
            field=models.IntegerField(verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='users',
            field=models.ManyToManyField(related_name='buddies', blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address', blank=True, null=True),
        ),
    ]
