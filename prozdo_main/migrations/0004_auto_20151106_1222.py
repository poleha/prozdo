# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prozdo_main', '0003_auto_20151106_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='mail_type',
            field=models.PositiveIntegerField(db_index=True, choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (3, 'Сброс пароля'), (4, 'Ответ на отзыв'), (5, 'Подтверждение электронного адреса')]),
        ),
    ]
