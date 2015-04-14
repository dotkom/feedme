# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('feedme', '0005_auto_20150218_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='group',
            field=models.ForeignKey(default=4, to='auth.Group'),
            preserve_default=False,
        ),
    ]
