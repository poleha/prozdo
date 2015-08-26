from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from .helper import make_alias
from django.core.urlresolvers import reverse


#<Constants***********************************************************

POST_TYPE_DRUG = 1
POST_TYPE_BLOG = 2
POST_TYPE_FORUM = 3
POST_TYPE_COSMETICS = 4
POST_TYPE_COMPONENT = 5
POST_TYPE_BRAND = 6
POST_TYPE_DRUG_USAGE_FORM = 7
POST_TYPE_COSMETICS_DOSAGE_FORM = 8
POST_TYPE_COSMETICS_LINE = 9
POST_TYPE_COSMETICS_USAGE_AREA = 10
POST_TYPE_DRUG_USAGE_AREA = 11
POST_TYPE_CATEGORY = 12


POST_TYPES = (
    (POST_TYPE_DRUG, 'Препарат'),
    (POST_TYPE_BLOG, 'Блог'),
    (POST_TYPE_FORUM, 'Форум'),
    (POST_TYPE_COMPONENT, 'Компонент'),
    (POST_TYPE_COSMETICS, 'Косметика'),
    (POST_TYPE_BRAND, 'Бренд'),
    (POST_TYPE_DRUG_USAGE_FORM, 'Форма выпуска препарата'),
    (POST_TYPE_COSMETICS_DOSAGE_FORM, 'Форма выпуска косметики'),
    (POST_TYPE_COSMETICS_LINE, 'Линия косметики'),
    (POST_TYPE_COSMETICS_USAGE_AREA, 'Область применения косметики'),
    (POST_TYPE_DRUG_USAGE_AREA, 'Област применения препарата'),
    (POST_TYPE_CATEGORY, 'Категория'),
)

#Constants>***********************************************************

#<Posts******************************************************************


class AbstractModel(models.Model):
    class Meta:
        abstract = True
    title = models.CharField(max_length=500, verbose_name='Название')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Post(AbstractModel):
    alias = models.CharField(max_length=800, blank=True)
    post_type = models.IntegerField(choices=POST_TYPES, verbose_name='Вид записи')

    def save(self, *args, **kwargs):
        if hasattr(self, 'title') and self.title and not self.alias:
            self.alias = make_alias(self.title)
        super().save(*args, **kwargs)


class Brand(Post):
    pass



class DrugDosageForm(Post):
    pass


class CosmeticsDosageForm(Post):
    pass


class CosmeticsLine(Post):
    pass

class CosmeticsUsageArea(Post):
    pass


class DrugUsageArea(Post):
    pass

class Category(Post):
    pass


class Component(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)

class Drug(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)
    features = models.TextField(verbose_name='Особенности', blank=True)
    indications = models.TextField(verbose_name='Показания', blank=True)
    priem = models.TextField(verbose_name='Схема приема', blank=True)
    dosage_form = models.TextField(verbose_name='Формы выпуска', blank=True)
    contra_indications = models.TextField(verbose_name='Противопоказания', blank=True)
    side_effects = models.TextField(verbose_name='Побочные эффекты', blank=True)
    compound = models.TextField(verbose_name='Состав', blank=True)

    dosage_forms = models.ManyToManyField(DrugDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(DrugUsageArea, verbose_name='Область применения')
    components = models.ManyToManyField(Component, verbose_name='Состав')


    def get_absolute_url(self):
        alias = self.alias.alias
        if alias:
            return reverse('post-detail', kwargs={'alias': alias})
        else:
            return reverse('drug-detail', kwargs={'pk': self.pk})


class Cosmetics(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)

    brand = models.ForeignKey(Brand, verbose_name='Бренд')
    line = models.ForeignKey(CosmeticsLine, verbose_name='Линия')
    dosage_forms = models.ManyToManyField(CosmeticsDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(CosmeticsUsageArea, verbose_name='Область применения')


class Blog(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)

class Forum(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)

#Post>*******************************************************************


class Comment(models.Model):
    post = models.ForeignKey(Post)
    body = models.TextField(verbose_name='Содержимое', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


HISTORY_TYPE_COMMENT_CREATED = 1
HISTORY_TYPE_COMMENT_SAVED = 2
HISTORY_TYPE_COMMENT_RATED = 3
HISTORY_TYPE_POST_CREATED = 4
HISTORY_TYPE_POST_SAVED = 5
HISTORY_TYPE_POST_RATED = 6
HISTORY_TYPE_COMMENT_COMPLAINT = 7
HISTORY_TYPE_POST_COMPLAINT = 8

HISTORY_TYPES = (
    (HISTORY_TYPE_COMMENT_CREATED, 'Комментарий создан'),
    (HISTORY_TYPE_COMMENT_SAVED, 'Комментарий сохранен'),
    (HISTORY_TYPE_COMMENT_RATED, 'Комментарий оценен'),
    (HISTORY_TYPE_POST_CREATED, 'Пост создан'),
    (HISTORY_TYPE_POST_SAVED, 'Пост сохранен'),
    (HISTORY_TYPE_POST_RATED, 'Пост оценен'),
    (HISTORY_TYPE_COMMENT_COMPLAINT, 'Жалоба на коммент'),
    (HISTORY_TYPE_POST_COMPLAINT, 'Жалоба на пост'),
)

class History(models.Model):
    post = models.ForeignKey(Post, related_name='history_post')
    history_type = models.IntegerField(choices=HISTORY_TYPES)
    author = models.ForeignKey(User, null=True, blank=True, related_name='history_author')
    user = models.ForeignKey(User, null=True, blank=True, related_name='history_user')
    created = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Component, null=True, blank=True, related_name='history_comment')
    user_points = models.PositiveIntegerField(default=0, blank=True)
    author_points = models.PositiveIntegerField(default=0, blank=True)


