# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import ckeditor_uploader.fields
import mptt.fields
import ckeditor.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, blank=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время изменения')),
                ('published', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время публикации')),
                ('username', models.CharField(verbose_name='Имя', max_length=256)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('post_mark', models.IntegerField(null=True, blank=True, verbose_name='Оценка', choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('body', models.TextField(verbose_name='Сообщение')),
                ('ip', models.CharField(db_index=True, max_length=300)),
                ('session_key', models.TextField(db_index=True, blank=True)),
                ('consult_required', models.BooleanField(db_index=True, default=False, verbose_name='Нужна консультация провизора')),
                ('status', models.IntegerField(db_index=True, verbose_name='Статус', choices=[(1, 'На согласовании'), (2, 'Опубликован')])),
                ('key', models.CharField(blank=True, max_length=128)),
                ('confirmed', models.BooleanField(db_index=True, default=False)),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(to='prozdo_main.Comment', blank=True, related_name='children', null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, blank=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время изменения')),
                ('history_type', models.IntegerField(db_index=True, choices=[(1, 'Комментарий создан'), (2, 'Комментарий сохранен'), (3, 'Комментарий оценен'), (4, 'Материал создан'), (5, 'Материал сохранен'), (6, 'Материал оценен'), (7, 'Жалоба на комментарий')])),
                ('user_points', models.PositiveIntegerField(default=0, blank=True)),
                ('ip', models.CharField(db_index=True, null=True, blank=True, max_length=300)),
                ('session_key', models.TextField(db_index=True, blank=True)),
                ('mark', models.IntegerField(null=True, blank=True, verbose_name='Оценка', choices=[(1, '1'), (1, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('deleted', models.BooleanField(db_index=True, default=False, verbose_name='Удалена')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='history_author', null=True)),
                ('comment', models.ForeignKey(to='prozdo_main.Comment', blank=True, related_name='history_comment', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, blank=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время изменения')),
                ('mail_type', models.PositiveIntegerField(db_index=True, choices=[(1, 'Подтверждение отзыва'), (2, 'Регистрация пользователя'), (1, 'Сброс пароля'), (4, 'Ответ на отзыв')])),
                ('subject', models.TextField()),
                ('body_html', models.TextField(default='', blank=True)),
                ('body_text', models.TextField(default='', blank=True)),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('ip', models.CharField(db_index=True, null=True, blank=True, max_length=300)),
                ('session_key', models.TextField(db_index=True, null=True, blank=True)),
                ('email_from', models.EmailField(db_index=True, max_length=254)),
                ('entity_id', models.CharField(db_index=True, blank=True, max_length=20)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, blank=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время изменения')),
                ('title', models.CharField(db_index=True, verbose_name='Название', max_length=500)),
                ('published', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время публикации')),
                ('alias', models.CharField(db_index=True, blank=True, verbose_name='Синоним', max_length=800)),
                ('post_type', models.IntegerField(db_index=True, verbose_name='Вид записи', choices=[(1, 'Препарат'), (2, 'Блог'), (3, 'Форум'), (5, 'Компонент'), (4, 'Косметика'), (6, 'Бренд'), (7, 'Форма выпуска препарата'), (8, 'Форма выпуска косметики'), (9, 'Линия косметики'), (10, 'Область применения косметики'), (11, 'Област применения препарата'), (12, 'Категория')])),
                ('status', models.IntegerField(db_index=True, default=1, verbose_name='Статус', choices=[(1, 'Проект'), (2, 'Опубликован')])),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, blank=True, verbose_name='Время создания')),
                ('updated', models.DateTimeField(db_index=True, null=True, blank=True, verbose_name='Время изменения')),
                ('role', models.PositiveIntegerField(db_index=True, default=1, blank=True, choices=[(1, 'Обычный пользователь'), (2, 'Автор'), (3, 'Врач'), (33, 'Админ')])),
                ('image', sorl.thumbnail.fields.ImageField(null=True, blank=True, verbose_name='Изображение', upload_to='user_profile')),
                ('receive_messages', models.BooleanField(db_index=True, default=True, verbose_name='Получать e-mail сообщения с сайта')),
                ('old_id', models.PositiveIntegerField(null=True, blank=True)),
                ('user', models.OneToOneField(related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
                ('short_body', models.TextField(blank=True, verbose_name='Анонс')),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Содержимое')),
                ('image', sorl.thumbnail.fields.ImageField(null=True, blank=True, verbose_name='Изображение', upload_to='blog')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(to='prozdo_main.Category', blank=True, related_name='children', null=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post', models.Model),
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
                ('body', ckeditor.fields.RichTextField(blank=True, verbose_name='Содержимое')),
                ('component_type', models.IntegerField(db_index=True, verbose_name='Тип компонента', choices=[(1, 'Витамин'), (2, 'Минеральное вещество'), (3, 'Растение'), (4, 'Прочее')])),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Cosmetics',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
                ('body', ckeditor.fields.RichTextField(blank=True, verbose_name='Содержимое')),
                ('image', sorl.thumbnail.fields.ImageField(null=True, blank=True, verbose_name='Изображение', upload_to='cosmetics')),
                ('brand', models.ForeignKey(to='prozdo_main.Brand', verbose_name='Бренд')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsLine',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='CosmeticsUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
                ('body', ckeditor.fields.RichTextField(blank=True, verbose_name='Описание')),
                ('features', ckeditor.fields.RichTextField(blank=True, verbose_name='Особенности')),
                ('indications', ckeditor.fields.RichTextField(blank=True, verbose_name='Показания')),
                ('application_scheme', ckeditor.fields.RichTextField(blank=True, verbose_name='Схема приема')),
                ('dosage_form', ckeditor.fields.RichTextField(blank=True, verbose_name='Формы выпуска')),
                ('contra_indications', ckeditor.fields.RichTextField(blank=True, verbose_name='Противопоказания')),
                ('side_effects', ckeditor.fields.RichTextField(blank=True, verbose_name='Побочные эффекты')),
                ('compound', ckeditor.fields.RichTextField(blank=True, verbose_name='Состав')),
                ('image', sorl.thumbnail.fields.ImageField(null=True, blank=True, verbose_name='Изображение', upload_to='drug')),
                ('category', mptt.fields.TreeManyToManyField(db_index=True, to='prozdo_main.Category', blank=True, verbose_name='Категория')),
                ('components', models.ManyToManyField(to='prozdo_main.Component', blank=True, verbose_name='Состав', related_name='drugs')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugDosageForm',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.CreateModel(
            name='DrugUsageArea',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='prozdo_main.Post')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=('prozdo_main.post',),
        ),
        migrations.AddField(
            model_name='history',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post', related_name='history_post'),
        ),
        migrations.AddField(
            model_name='history',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='history_user', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(to='prozdo_main.Post', related_name='comments'),
        ),
        migrations.AddField(
            model_name='comment',
            name='updater',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='updated_comments', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='comments', null=True),
        ),
        migrations.AddField(
            model_name='drug',
            name='dosage_forms',
            field=models.ManyToManyField(to='prozdo_main.DrugDosageForm', verbose_name='Формы выпуска'),
        ),
        migrations.AddField(
            model_name='drug',
            name='usage_areas',
            field=models.ManyToManyField(to='prozdo_main.DrugUsageArea', verbose_name='Область применения'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='dosage_forms',
            field=models.ManyToManyField(to='prozdo_main.CosmeticsDosageForm', verbose_name='Формы выпуска'),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='line',
            field=models.ForeignKey(to='prozdo_main.CosmeticsLine', blank=True, verbose_name='Линейка', null=True),
        ),
        migrations.AddField(
            model_name='cosmetics',
            name='usage_areas',
            field=models.ManyToManyField(to='prozdo_main.CosmeticsUsageArea', verbose_name='Область применения'),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=mptt.fields.TreeManyToManyField(db_index=True, to='prozdo_main.Category', verbose_name='Категория'),
        ),
    ]
