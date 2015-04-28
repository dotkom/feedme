# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedme', '0007_poll_group'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'permissions': (('vote_poll', 'Vote Poll'),)},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'get_latest_by': 'date', 'permissions': (('view_order', 'View Order'), ('edit_order', 'Edit Order'))},
        ),
        migrations.AlterModelOptions(
            name='orderline',
            options={'verbose_name': 'Orderline', 'verbose_name_plural': 'Orderlines', 'permissions': (('view_order', 'View Order'), ('edit_order', 'Edit Order'))},
        ),
        migrations.AlterModelOptions(
            name='poll',
            options={'permissions': (('view_poll', 'View Poll'), ('edit_poll', 'Edit Poll'))},
        ),
    ]
