# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20151106_1222'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={},
        ),
        migrations.AlterModelOptions(
            name='component',
            options={},
        ),
        migrations.AlterModelOptions(
            name='cosmetics',
            options={},
        ),
        migrations.AlterModelOptions(
            name='cosmeticsdosageform',
            options={},
        ),
        migrations.AlterModelOptions(
            name='cosmeticsline',
            options={},
        ),
        migrations.AlterModelOptions(
            name='cosmeticsusagearea',
            options={},
        ),
        migrations.AlterModelOptions(
            name='drug',
            options={},
        ),
        migrations.AlterModelOptions(
            name='drugdosageform',
            options={},
        ),
        migrations.AlterModelOptions(
            name='drugusagearea',
            options={},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(null=True, verbose_name='Изображение', upload_to='user_profile', blank=True),
        ),
    ]
