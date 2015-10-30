# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prozdo_main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='delete_mark',
            field=models.BooleanField(default=False, verbose_name='Пометка удаления', db_index=True),
        ),
    ]
