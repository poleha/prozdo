# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_comment_delete_mark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='mail_type',
            field=models.PositiveIntegerField(choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв'), (5, 'Подтверждение электронного адреса')], db_index=True),
        ),
    ]
