from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from .helper import make_alias
from django.core.urlresolvers import reverse


class PostMixin(models.Model):
    class Meta:
        abstract = True

    post_cls = models.CharField(max_length=100)
    post_id = models.PositiveIntegerField()

class Alias(PostMixin):
    alias = models.CharField(max_length=800, blank=True)


class AliasMixin(models.Model):
    class Meta:
        abstract = True
    alias = models.OneToOneField('Alias', null=True, blank=True)

    def save(self, *args, create_alias=True, **kwargs):
        super().save(*args, **kwargs)
        if create_alias:
            alias, created = Alias.objects.get_or_create(post_cls=type(self).__name__, post_id=self.pk)
            if hasattr(self, 'title') and self.title and not alias.alias:
                alias.alias = make_alias(self.title)
                alias.save()
            self.alias = alias
            self.save(create_alias=False)



"""
def save_alias(sender, instance, created, **kwargs):
    if instance.title and not instance.alias:
        instance.alias = transliterate(instance.title)


post_save.connect(save_alias, sender=Product)
"""

class AbstractModel(models.Model):
    class Meta:
        abstract = True
    title = models.CharField(max_length=500, verbose_name='Название')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Brand(AliasMixin):
    title = models.CharField(max_length=500, verbose_name='Название')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

#class Post(models.Model):


class DrugDosageForm(AbstractModel):
    pass


class CosteticsDosageForm(AbstractModel):
    pass


class CosmeticsLine(AbstractModel):
    pass

class CosmeticsUsageArea(AbstractModel):
    pass


class DrugUsageArea(AbstractModel):
    pass

class Category(AbstractModel):
    pass


class Component(AliasMixin, AbstractModel):
    body = models.TextField(verbose_name='Содержимое', blank=True)

class Drug(AliasMixin, AbstractModel):
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


class Cosmetics(AliasMixin, AbstractModel):
    body = models.TextField(verbose_name='Содержимое', blank=True)

    brand = models.ForeignKey(Brand, verbose_name='Бренд')
    line = models.ForeignKey(CosmeticsLine, verbose_name='Линия')
    dosage_forms = models.ManyToManyField(CosteticsDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(CosmeticsUsageArea, verbose_name='Область применения')


class Blog(AliasMixin, AbstractModel):
    body = models.TextField(verbose_name='Содержимое', blank=True)

class Forum(AbstractModel):
    body = models.TextField(verbose_name='Содержимое', blank=True)




class Comment(PostMixin):
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

class History(PostMixin):
    history_type = models.IntegerField(choices=HISTORY_TYPES)
    author = models.ForeignKey(User, null=True, blank=True, related_name='history_author')
    user = models.ForeignKey(User, null=True, blank=True, related_name='history_user')
    created = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Component, null=True, blank=True)
    user_points = models.PositiveIntegerField(default=0, blank=True)
    author_points = models.PositiveIntegerField(default=0, blank=True)


