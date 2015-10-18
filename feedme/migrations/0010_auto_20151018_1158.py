# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0009_auto_20150926_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(related_name='bruker', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='email',
            field=models.EmailField(max_length=75, null=True, verbose_name='email address', blank=True),
            preserve_default=True,
        ),
    ]
