from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.db.models.signals import post_save, pre_save
from .helper import make_alias, get_client_ip, cut_text, comment_body_ok, comment_author_ok
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum, Count
from multi_image_upload.models import MyImageField
from django.conf import settings
from math import ceil


#<Constants***********************************************************

POST_TYPE_DRUG = 1
POST_TYPE_BLOG = 2
POST_TYPE_FORUM = 3
POST_TYPE_COSMETICS = 4
POST_TYPE_COMPONENT = 5
POST_TYPE_BRAND = 6
POST_TYPE_DRUG_DOSAGE_FORM = 7
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
    (POST_TYPE_DRUG_DOSAGE_FORM, 'Форма выпуска препарата'),
    (POST_TYPE_COSMETICS_DOSAGE_FORM, 'Форма выпуска косметики'),
    (POST_TYPE_COSMETICS_LINE, 'Линия косметики'),
    (POST_TYPE_COSMETICS_USAGE_AREA, 'Область применения косметики'),
    (POST_TYPE_DRUG_USAGE_AREA, 'Област применения препарата'),
    (POST_TYPE_CATEGORY, 'Категория'),
)

USER_ROLE_REGULAR = 1
USER_ROLE_AUTHOR = 2
USER_ROLE_DOCTOR = 3
USER_ROLE_ADMIN = 33

USER_ROLES = (
    (USER_ROLE_REGULAR, 'Обычный пользователь'),
    (USER_ROLE_AUTHOR, 'Автор'),
    (USER_ROLE_DOCTOR, 'Врач'),
    (USER_ROLE_ADMIN, 'Админ'),
)


POST_MARKS_FOR_COMMENT = (
    (1, '1'),
    (1, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)

COMMENT_STATUS_PENDING_APPROVAL = 1
COMMENT_STATUS_PUBLISHED = 2

COMMENT_STATUSES = (
    (COMMENT_STATUS_PENDING_APPROVAL, 'На согласовании'),
    (COMMENT_STATUS_PUBLISHED, 'Опубликован'),
)


POST_STATUS_PROJECT = 1
POST_STATUS_PUBLISHED = 2


POST_STATUSES = (
    (POST_STATUS_PROJECT, 'Проект'),
    (POST_STATUS_PUBLISHED, 'Опубликован'),
)






#Constants>***********************************************************

#<Posts******************************************************************
class SuperModel(models.Model):
    class Meta:
        abstract = True
    @property
    def saved_version(self):
        if self.pk:
            try:
                saved_version = type(self).objects.get(pk=self.pk)
            except:
                saved_version = None
        else:
            saved_version = None
        return saved_version

class AbstractModel(SuperModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=500, verbose_name='Название')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PostQueryset(models.QuerySet):
    def get_available(self):
        queryset = self.filter(status=POST_STATUS_PUBLISHED)
        return queryset


class PostManager(models.manager.BaseManager.from_queryset(PostQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class Post(AbstractModel):
    alias = models.CharField(max_length=800, blank=True)
    post_type = models.IntegerField(choices=POST_TYPES, verbose_name='Вид записи')
    status = models.IntegerField(choices=POST_STATUSES, verbose_name='Статус', default=POST_STATUS_PROJECT)
    objects = PostManager()

    def get_post_type(self):
        if type(self) == Drug:
            return POST_TYPE_DRUG
        elif type(self) == Blog:
            return POST_TYPE_BLOG
        elif type(self) == Forum:
            return POST_TYPE_FORUM
        elif type(self) == Component:
            return POST_TYPE_COMPONENT
        elif type(self) == Cosmetics:
            return POST_TYPE_COSMETICS
        elif type(self) == Brand:
            return POST_TYPE_BRAND
        elif type(self) == DrugDosageForm:
            return POST_TYPE_DRUG_DOSAGE_FORM
        elif type(self) == CosmeticsDosageForm:
            return POST_TYPE_COSMETICS_DOSAGE_FORM
        elif type(self) == CosmeticsLine:
            return POST_TYPE_COSMETICS_LINE
        elif type(self) == CosmeticsUsageArea:
            return POST_TYPE_COSMETICS_USAGE_AREA
        elif type(self) == DrugUsageArea:
            return POST_TYPE_DRUG_USAGE_AREA
        elif type(self) == Category:
            return POST_TYPE_CATEGORY

    @property
    def obj(self):
        if self.post_type == POST_TYPE_DRUG:
            return self.drug
        elif self.post_type == POST_TYPE_COMPONENT:
            return self.component
        elif self.post_type == POST_TYPE_BLOG:
            return self.blog
        elif self.post_type == POST_TYPE_FORUM:
            return self.forum
        elif self.post_type == POST_TYPE_COSMETICS:
            return self.cosmetics
        elif self.post_type == POST_TYPE_BRAND:
            return self.brand
        elif self.post_type == POST_TYPE_DRUG_DOSAGE_FORM:
            return self.drug_usage_form
        elif self.post_type == POST_TYPE_COSMETICS_DOSAGE_FORM:
            return self.cosmetics_dosage_form
        elif self.post_type == POST_TYPE_COSMETICS_LINE:
            return self.cosmetics_line
        elif self.post_type == POST_TYPE_COSMETICS_USAGE_AREA:
            return self.cosmetics_usage_area
        elif self.post_type == POST_TYPE_DRUG_USAGE_AREA:
            return self.drug_usage_area
        elif self.post_type == POST_TYPE_CATEGORY:
            return self.category

    def get_absolute_url(self):
        alias = self.alias
        if alias:
            return reverse('post-detail-alias', kwargs={'alias': alias})
        else:
            return reverse('post-detail-pk', kwargs={'pk': self.pk})

    def get_mark_by_request(self, request):
        user = request.user
        if user.is_authenticated():
            try:
                mark = History.objects.get(user=user, history_type=HISTORY_TYPE_POST_RATED).mark
            except:
                mark = None
        else:
            try:
                mark = History.objects.get(ip=get_client_ip(request), history_type=HISTORY_TYPE_POST_RATED, user=None).mark
            except:
                mark = None
        return mark

    @property
    def average_mark(self):
        try:
            mark = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED).aggregate(Sum('mark'))['mark__sum']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark

    @property
    def marks_count(self):
        try:
            count = History.objects.filter(post=self, history_type=HISTORY_TYPE_POST_RATED).aggregate(Count('mark'))['mark__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    @property
    def published_comments_count(self):
        return self.comments.get_available().count()

    @property
    def last_comment_date(self):
        try:
            last_comment = self.comments.get_available().latest('created')
            date = last_comment.created
        except:
            date = None
        return date

    def save(self, *args, **kwargs):
        #saved_version = self.saved_version
        if hasattr(self, 'title') and self.title and not self.alias:
            self.alias = make_alias(self.title)
        if self.alias:
            alias_is_busy = Post.objects.filter(alias=self.alias).exclude(pk=self.pk)
            if alias_is_busy:
                raise ValidationError('Синоним {0} занят'.format(self.alias))

        self.post_type = self.get_post_type()
        super().save(*args, **kwargs)
        History.save_history(history_type=HISTORY_TYPE_POST_CREATED, post=self)

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
    application_scheme = models.TextField(verbose_name='Схема приема', blank=True)
    dosage_form = models.TextField(verbose_name='Формы выпуска', blank=True)
    contra_indications = models.TextField(verbose_name='Противопоказания', blank=True)
    side_effects = models.TextField(verbose_name='Побочные эффекты', blank=True)
    compound = models.TextField(verbose_name='Состав', blank=True)
    image = MyImageField(verbose_name='Изображение', upload_to='drug',
                         thumb_settings=settings.DRUG_THUMB_SETTINGS)

    dosage_forms = models.ManyToManyField(DrugDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(DrugUsageArea, verbose_name='Область применения')
    components = models.ManyToManyField(Component, verbose_name='Состав', blank=True)
    objects = PostManager()


class Cosmetics(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)
    image = MyImageField(verbose_name='Изображение', upload_to='cosmetics',
                         thumb_settings=settings.COSMETICS_THUMB_SETTINGS)

    brand = models.ForeignKey(Brand, verbose_name='Бренд')
    line = models.ForeignKey(CosmeticsLine, verbose_name='Линия')
    dosage_forms = models.ManyToManyField(CosmeticsDosageForm, verbose_name='Формы выпуска')
    usage_areas = models.ManyToManyField(CosmeticsUsageArea, verbose_name='Область применения')


class Blog(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)
    image = MyImageField(verbose_name='Изображение', upload_to='blog',
                         thumb_settings=settings.BLOG_THUMB_SETTINGS)

class Forum(Post):
    body = models.TextField(verbose_name='Содержимое', blank=True)

#Post>*******************************************************************



class CommentQueryset(models.QuerySet):
    def get_available(self):
        queryset = self.filter(status=COMMENT_STATUS_PUBLISHED)
        return queryset


class CommentManager(models.manager.BaseManager.from_queryset(CommentQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset



class Comment(models.Model):
    class Meta:
        ordering = ['created']
    post = models.ForeignKey(Post, related_name='comments')
    username = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(verbose_name='E-Mail')
    post_mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')
    body = models.TextField(verbose_name='Сообщение')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, blank=True)
    ip = models.CharField(max_length=15)
    consult_required = models.BooleanField(default=False, verbose_name='Нужна консультация провизора')
    parent = models.ForeignKey('Comment', verbose_name='В ответ на', null=True, blank=True, related_name='childs')
    status = models.IntegerField(choices=COMMENT_STATUSES, verbose_name='Статус')

    objects = CommentManager()

    def __str__(self):
        return self.short_body


    @property
    def page(self):
        comments = self.post.comments.get_available().order_by('-created')
        #count = comments.count()
        #pages_count = ceil(count / page_size)
        page_size = settings.POST_COMMENTS_PAGE_SIZE
        comments_tuple = tuple(comments)
        index = comments_tuple.index(self) + 1
        current_page = ceil(index / page_size)
        return current_page



    def all_childs_pks(self, cur=None, pks=None):
        if cur is None:
            cur = self
            pks = []
        else:
            pks.append(cur.pk)
        for child in cur.childs.all():
            self.all_childs_pks(cur=child, pks=pks)
        return pks

    @property
    def all_childs(self):
        return type(self).objects.filter(pk__in=self.all_childs_pks())

    @property
    def available_childs(self):
        return self.all_childs.get_available()


    @property
    def short_body(self):
        return cut_text(self.body)

    @property
    def get_level(self):
        if hasattr(self, 'level') and self.level:
            return self.level
        else:
            return 1

    @property
    def comment_mark(self):
        try:
            mark = History.objects.filter(comment=self, history_type=HISTORY_TYPE_COMMENT_RATED).aggregate(Sum('author_points'))['author_points__sum']
            if mark is None:
                mark = 0
        except:
            mark = 0
        return mark

    def get_childs_tree(self, cur=None, level=2):
        tree = []
        if cur is None:
            cur = self
        else:
            tree.append(cur)
        for child in cur.childs.get_available().order_by('created'):
            child.level = level
            tree += child.get_childs_tree(child, level+1)
        return tree

    def get_absolute_url(self):
        return '{0}/comment/{1}#c{1}'.format(self.post.get_absolute_url(), self.pk)


    def get_status(self):
        if self.user and self.user.is_authenticated():
            return COMMENT_STATUS_PUBLISHED
        else:
            if comment_body_ok(self.body) and comment_author_ok(self.username):
                return COMMENT_STATUS_PUBLISHED
            else:
                return COMMENT_STATUS_PENDING_APPROVAL

    @property
    def complain_count(self):
        try:
            count = History.objects.filter(comment=self, history_type=HISTORY_TYPE_COMMENT_COMPLAINT).aggregate(Count('pk'))['pk__count']
            if count is None:
                count = 0
        except:
            count = 0
        return count

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        History.save_history(history_type=HISTORY_TYPE_COMMENT_CREATED, post=self.post, comment=self, ip=self.ip, user=self.user)

    def performed_action(self, history_type, user=None, ip=None, request=None):
        if not ip and request:
            ip = get_client_ip(request)
        if not user and request:
            user = request.user

        if user and user.is_authenticated():
            hist_exists = History.objects.filter(history_type=history_type, comment=self, user=user).exists()
        else:
            hist_exists_by_ip = History.objects.filter(history_type=history_type, comment=self, ip=ip).exists()
            hist_exists_by_key = History.objects.filter(history_type=history_type, comment=self).exists()
            hist_exists = hist_exists_by_ip or hist_exists_by_key

        return hist_exists

    def can_perform_action(self, history_type, user=None, ip=None, request=None):
        return not self.performed_action(history_type=history_type, user=user, ip=ip, request=request) and not self.is_author(user=user, ip=ip, request=request)

    def can_undo_action(self, history_type, user):
        if user.is_authenticated():
            res = self.performed_action(history_type=history_type, user=user)
        else:
            res = False
        return res


    def is_author(self, user=None, ip=None, request=None):
        if not ip and request:
            ip = get_client_ip(request)
        if not user and request:
            user = request.user
        if user and user.is_authenticated():
            res = self.user == user
        else:
            res = self.ip == ip
        return res



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

HISTORY_TYPES_POINTS = {
HISTORY_TYPE_COMMENT_CREATED: 3,
HISTORY_TYPE_COMMENT_SAVED: 0,
HISTORY_TYPE_COMMENT_RATED: 1,
HISTORY_TYPE_POST_CREATED: 5,
HISTORY_TYPE_POST_SAVED: 0,
HISTORY_TYPE_POST_RATED: 1,
HISTORY_TYPE_COMMENT_COMPLAINT: 0,
HISTORY_TYPE_POST_COMPLAINT: 0,
}


class History(models.Model):
    post = models.ForeignKey(Post, related_name='history_post')
    history_type = models.IntegerField(choices=HISTORY_TYPES)
    author = models.ForeignKey(User, null=True, blank=True, related_name='history_author')
    user = models.ForeignKey(User, null=True, blank=True, related_name='history_user')
    comment = models.ForeignKey(Comment, null=True, blank=True, related_name='history_comment')
    user_points = models.PositiveIntegerField(default=0, blank=True)
    author_points = models.PositiveIntegerField(default=0, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=15, null=True, blank=True)
    mark = models.IntegerField(choices=POST_MARKS_FOR_COMMENT, blank=True, null=True, verbose_name='Оценка')

    @staticmethod
    def get_points(history_type):
        return HISTORY_TYPES_POINTS[history_type]

    def __str__(self):
        return "{0} - {1} - {2}".format(self.history_type, self.post, self.comment)

    @staticmethod
    def save_history(history_type, post, user=None, ip=None, comment=None, mark=None):
        if hasattr(post, 'user'):
            post_author = post.user
        else:
            post_author = None

        if user and not user.is_authenticated():
            user = None

        if isinstance(mark, str):
            mark = int(mark)

        if mark is None and comment is not None and comment.post_mark:
            mark = comment.post_mark

        if history_type == HISTORY_TYPE_POST_CREATED:
            hist_exists = History.objects.filter(history_type=history_type, post=post).exists()
            if not hist_exists:
                History.objects.create(history_type=history_type, post=post, user=user,
                                       user_points=History.get_points(history_type), ip=ip, author=post_author)
            else:
                History.save_history(HISTORY_TYPE_POST_SAVED, post, user, ip, comment)
        elif history_type == HISTORY_TYPE_POST_SAVED:
            History.objects.create(history_type=history_type, post=post, user=user, ip=ip, author=post_author)
        elif history_type == HISTORY_TYPE_COMMENT_CREATED:
            hist_exists = History.objects.filter(history_type=history_type, comment=comment).exists()
            if not hist_exists:

                History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=post_author)
            else:
                History.save_history(HISTORY_TYPE_COMMENT_SAVED, post, user, ip, comment)
        elif history_type == HISTORY_TYPE_COMMENT_SAVED:
            History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                   user_points=History.get_points(history_type), author=post_author)
        elif history_type in [HISTORY_TYPE_COMMENT_RATED, HISTORY_TYPE_COMMENT_COMPLAINT]:
            if history_type == HISTORY_TYPE_COMMENT_RATED:
                author_points = 1
            else:
                author_points = 0

            if comment.can_perform_action(history_type=history_type, user=user, ip=ip):
                History.objects.create(history_type=history_type, post=post, user=user, comment=comment, ip=ip,
                                       user_points=History.get_points(history_type),
                                       author=comment.user, author_points=author_points)
        elif history_type == HISTORY_TYPE_POST_RATED:
            if user and user.is_authenticated():
                hist_exists = History.objects.filter(history_type=history_type, post=post, user=user).exists()
            else:
                hist_exists = History.objects.filter(history_type=history_type, post=post, ip=ip, user=user).exists()

            if not hist_exists and mark and mark > 0:
                History.objects.create(history_type=history_type, post=post, user=user, ip=ip, comment=comment,
                                   user_points=History.get_points(history_type), author=post_author, mark=mark)

        #При сохранении отзыва сохраняем оценку поста
        if history_type in [HISTORY_TYPE_COMMENT_CREATED, HISTORY_TYPE_COMMENT_SAVED] and mark:


            History.save_history(HISTORY_TYPE_POST_RATED, post, user=user, ip=ip, comment=comment, mark=mark)

class UserProfile(SuperModel):
    # required by the auth model
    user = models.OneToOneField(User, related_name='user_profile')  # reverse returns single object, not queryset
    role = models.PositiveIntegerField(choices=USER_ROLES, default=USER_ROLE_REGULAR, blank=True)
    image = MyImageField(verbose_name='Изображение', upload_to='user_profile',
                         thumb_settings=settings.USER_PROFILE_THUMB_SETTINGS, null=True, blank=True)

    def __str__(self):
        return 'Профиль пользователя {0}, pk={1}'.format(self.user.username, self.user.pk)

    @classmethod
    def get_profile(cls, user):
        user_profile, created = cls.objects.get_or_create(user=user)
        if created:
            user_profile.save()
        return user_profile

    def save(self, *args, **kwargs):
        self.role = USER_ROLE_REGULAR
        if self.user.is_staff:
            self.role = USER_ROLE_ADMIN

        super().save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        profile.save()


post_save.connect(create_user_profile, sender=User)



def is_regular(self):
    if self.user_profile.role == USER_ROLE_REGULAR:
        return True
    else:
        return False

def get_user_image(self):
    return self.user_profile.image

User.is_regular = property(is_regular)
User.image = property(get_user_image)
AnonymousUser.is_regular = True
AnonymousUser.image = None