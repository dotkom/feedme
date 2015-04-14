# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('feedme', '0006_order_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='group',
            field=models.ForeignKey(default=4, to='auth.Group'),
            preserve_default=False,
        ),
    ]
