# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prozdo_main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alias',
            name='alias',
            field=models.CharField(blank=True, max_length=800),
        ),
    ]
