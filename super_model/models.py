from django.db import models
from django.utils import timezone
from cache.models import CachedModelMixin
from mptt.models import MPTTModel, TreeForeignKey
from mptt.querysets import TreeQuerySet
from django.contrib.auth.models import User, AnonymousUser
from cache.decorators import cached_property
from django.conf import settings
from django.core.urlresolvers import reverse
from math import ceil
from helper import helper
from django.utils.html import strip_tags
import re
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string
from django.db.models import ImageField


class SuperModel(models.Model):
    created = models.DateTimeField(blank=True, verbose_name='Время создания', db_index=True)
    updated = models.DateTimeField(blank=True, null=True, verbose_name='Время изменения', db_index=True)

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

    def save(self, *args, **kwargs):
        if not self.pk and not self.created:
            self.created = timezone.now()
        if self.pk and not self.updated:
            self.updated = timezone.now()
        super().save(*args, **kwargs)


def class_with_published_mixin(published_status):
    class PublishedModelMixin(models.Model):
        class Meta:
            abstract = True

        published = models.DateTimeField(null=True, blank=True, verbose_name='Время публикации', db_index=True)

        def save(self, *args, **kwargs):
            if self.status == published_status and not self.published:
                self.published = timezone.now()
            super().save(*args, **kwargs)

    return PublishedModelMixin


COMMENT_STATUS_PENDING_APPROVAL = 1
COMMENT_STATUS_PUBLISHED = 2

COMMENT_STATUSES = (
    (COMMENT_STATUS_PENDING_APPROVAL, 'На согласовании'),
    (COMMENT_STATUS_PUBLISHED, 'Опубликован'),
)


class CommentTreeQueryset(TreeQuerySet):
    def get_available(self):
        queryset = self.filter(status=COMMENT_STATUS_PUBLISHED)
        return queryset



class CommentManager(models.manager.BaseManager.from_queryset(CommentTreeQueryset)):
    use_for_related_fields = True


class SuperComment(SuperModel, CachedModelMixin, MPTTModel, class_with_published_mixin(COMMENT_STATUS_PUBLISHED)):
    class Meta:
        abstract = True

    username = models.CharField(max_length=256, verbose_name='Имя')
    email = models.EmailField(verbose_name='E-Mail')
    body = models.TextField(verbose_name='Сообщение')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comments', db_index=True)
    ip = models.CharField(max_length=300, db_index=True)
    session_key = models.TextField(blank=True, null=True, db_index=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    status = models.IntegerField(choices=COMMENT_STATUSES, verbose_name='Статус', db_index=True)
    updater = models.ForeignKey(User, null=True, blank=True, related_name='updated_comments')
    key = models.CharField(max_length=128, blank=True)

    objects = CommentManager()

    @cached_property
    def has_avaliable_children(self):
        return self.children.get_available().exists()


    @property
    def get_tree_level(self):
        if hasattr(self, 'tree_level'):
            return self.tree_level
        else:
            return 0

    @property
    def update_url(self):
        return reverse('comment-update', kwargs={'pk': self.pk})


    @cached_property
    def get_children_tree(self):
        return self._get_children_tree()

    def _get_children_tree(self, cur=None, level=1):
        tree = []
        if cur is None:
            cur = self
        else:
            tree.append(cur)
        for child in cur.children.get_available().order_by('created'):
            child.tree_level = level
            tree += child._get_children_tree(child, level+1)
        return tree

    @property
    def page(self):
        comments = self.post.comments.get_available().order_by('-created')
        #count = comments.count()
        #pages_count = ceil(count / page_size)
        page_size = settings.POST_COMMENTS_PAGE_SIZE
        comments_tuple = tuple(comments)
        try:
            index = comments_tuple.index(self) + 1
            current_page = ceil(index / page_size)
        except:
            current_page = 1
        return current_page

    @cached_property
    def available_children(self):
        return self.get_descendants().filter(status=COMMENT_STATUS_PUBLISHED)

    @cached_property
    def available_children_count(self):
        return self.available_children.count()

    @cached_property
    def available_first_level_children(self):
        return type(self).objects.filter(parent=self)

    @property
    def short_body(self):
        return helper.cut_text(strip_tags(self.body))

    @cached_property
    def _cached_get_absolute_url(self):
        if self.status == COMMENT_STATUS_PUBLISHED:
            #return '{0}comment/{1}#c{1}'.format(self.post.get_absolute_url(), self.pk)
            return reverse('post-detail-pk-comment', kwargs={'pk': self.post.pk, 'comment_pk': self.pk}) + '#c' + str(self.pk)
        else:
            return self.post.get_absolute_url()

    def get_absolute_url(self):
        return self._cached_get_absolute_url

    def clean(self):
        if not self.pk:
                try:
                    comment = type(self).objects.filter(body=self.body, session_key=self.session_key, user=self.user, post=self.post).latest('created')
                except:
                    comment = None
                if comment:
                    delta = timezone.now() - comment.created
                    if delta.seconds < 180:
                        raise ValidationError('Повторный отзыв')

    def generate_key(self):
        if self.key:
            return self.key
        else:
            return helper.generate_key(128)

    def get_status(self):
        if self.user and self.user.user_profile.can_publish_comment:
            return COMMENT_STATUS_PUBLISHED
        else:
            if (helper.comment_body_ok(self.body) and helper.comment_author_ok(self.username)) or self.email in (settings.AUTO_APPROVE_EMAILS + settings.AUTO_DONT_APPROVE_EMAILS):
                return COMMENT_STATUS_PUBLISHED
            else:
                return COMMENT_STATUS_PENDING_APPROVAL


    def delete(self, *args, **kwargs):
        post = self.post
        user = self.user
        ancestors = list(self.get_ancestors())
        descendants = list(self.get_descendants())
        super().delete(*args, **kwargs)
        if post:
            #invalidate_obj(post.obj)
            post.obj.full_invalidate_cache()
        if user:
            #invalidate_obj(user.user_profile)
            user.user_profile.full_invalidate_cache()
        for ancestor in ancestors:
            ancestor.full_invalidate_cache()
            #invalidate_obj(ancestor)
        for descendant in descendants:
            descendant.full_invalidate_cache()
            #invalidate_obj(descendant)


    def save(self, *args, **kwargs):
        if not self.confirmed:
            if self.user and self.user.email_confirmed:
                self.confirmed = True
            elif self.email in settings.AUTO_APPROVE_EMAILS:
                self.confirmed = True

        if not self.key:
            self.key = self.generate_key()

        if not self.user or self.user.is_regular:
            self.body = strip_tags(self.body)
        super().save(*args, **kwargs)


class AbstractModel(SuperModel, CachedModelMixin):
    class Meta:
        abstract = True
        ordering = ('title', )
    title = models.CharField(max_length=500, verbose_name='Название', db_index=True)

    def __str__(self):
        return self.title

    def type_str(self):
        raise NotImplemented


POST_STATUS_PROJECT = 1
POST_STATUS_PUBLISHED = 2


POST_STATUSES = (
    (POST_STATUS_PROJECT, 'Проект'),
    (POST_STATUS_PUBLISHED, 'Опубликован'),
)


class PostQueryset(models.QuerySet):
    def get_available(self):
        queryset = self.filter(status=POST_STATUS_PUBLISHED)
        return queryset


class PostManager(models.manager.BaseManager.from_queryset(PostQueryset)):
    use_for_related_fields = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

class SuperPost(AbstractModel, class_with_published_mixin(POST_STATUS_PUBLISHED)):
    class Meta:
        abstract = True
    alias = models.CharField(max_length=800, blank=True, verbose_name='Синоним', db_index=True)
    status = models.IntegerField(choices=POST_STATUSES, verbose_name='Статус', default=POST_STATUS_PROJECT, db_index=True)

    objects = PostManager()

    history_class = None

    @cached_property
    def last_modified(self):
        try:
            return self.history_class.objects.filter(post=self).latest('created').created
        except:
            if self.updated:
                return self.updated
            elif self.created:
                return self.created
            else:
                return None

    @cached_property
    def published_comments_count(self):
        return self.comments.get_available().count()

    @cached_property
    def last_comment_date(self):
        try:
            last_comment = self.comments.get_available().latest('created')
            date = last_comment.created
        except:
            date = None
        return date


    def make_alias(self):
        return helper.make_alias(self.title)

    def clean(self):
        if self.alias:
            try:
                self.alias.encode('ascii')
            except:
                raise ValidationError('Недопустимые символы в синониме {0}'.format(self.alias))

            result = re.match('[a-z0-9_\-]{1,}', self.alias)
            if not result:
                raise ValidationError('Недопустимые символы в синониме')
    def save(self, *args, **kwargs):
        self.clean()
        self.title = helper.trim_title(self.title)
        #saved_version = self.saved_version
        if hasattr(self, 'title') and self.title and not self.alias:
            self.alias = self.make_alias()
        if self.alias:
            BASE_POST_CLASS = import_string(settings.BASE_POST_CLASS)
            alias_is_busy = BASE_POST_CLASS.objects.filter(alias=self.alias).exclude(pk=self.pk)
            if alias_is_busy:
                raise ValidationError('Синоним {0} занят'.format(self.alias))

        self.post_type = self.get_post_type()
        super().save(*args, **kwargs)

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


class SuperUserProfile(SuperModel, CachedModelMixin):
    class Meta:
        abstract = True

    user = models.OneToOneField(User, related_name='user_profile', db_index=True)  # reverse returns single object, not queryset
    role = models.PositiveIntegerField(choices=USER_ROLES, default=USER_ROLE_REGULAR, blank=True, db_index=True)
    image = ImageField(verbose_name='Изображение', upload_to='user_profile', blank=True, null=True)
    receive_messages = models.BooleanField(default=True, verbose_name='Получать e-mail сообщения с сайта', blank=True, db_index=True)

    @property
    def can_publish_comment(self):
        if self.user.is_admin or self.user.is_author or self.user.is_doctor or self.get_user_karm >= settings.PUBLISH_COMMENT_WITHOUT_APPROVE_KARM:
            return True
        else:
            return False

    def __str__(self):
        return 'Профиль пользователя {0}, pk={1}'.format(self.user.username, self.user.pk)

    @classmethod
    def get_profile(cls, user):
        user_profile, created = cls.objects.get_or_create(user=user)
        if created:
            user_profile.save()
        return user_profile

    def save(self, *args, **kwargs):
        if self.user.is_staff:
            self.role = USER_ROLE_ADMIN

        super().save(*args, **kwargs)
        #invalidate_obj(self.user)



def is_regular(self):
    if self.user_profile.role == USER_ROLE_REGULAR:
        return True
    else:
        return False

def get_user_image(self):
    return self.user_profile.image

@property
def karm_history(self):
    return self.user_profile.karm_history

@property
def activity_history(self):
    return self.user_profile.activity_history

@property
def get_user_activity(self):
    return self.user_profile.get_user_activity

@property
def get_user_karm(self):
    return self.user_profile.get_user_karm


@property
def get_email_confirmed(self):
    return self.user_profile.get_email_confirmed()

User.is_regular = property(is_regular)
User.image = property(get_user_image)
User.karm_history = karm_history
User.activity_history = activity_history
User.karm = get_user_karm
User.get_karm_url = lambda self: reverse('user-karma', kwargs={'pk': self.pk})
User.get_comments_url = lambda self: reverse('user-comments', kwargs={'pk': self.pk})
User.get_activity_url = lambda self: reverse('user-activity', kwargs={'pk': self.pk})
User.get_absolute_url = lambda self: reverse('user-detail', kwargs={'pk': self.pk})

User.activity = get_user_activity
User.email_confirmed = get_email_confirmed

User.is_admin = property(lambda self: self.user_profile.role == USER_ROLE_ADMIN)
User.is_author = property(lambda self: self.user_profile.role == USER_ROLE_AUTHOR)
User.is_regular = property(lambda self: self.user_profile.role == USER_ROLE_REGULAR)
User.is_doctor = property(lambda self: self.user_profile.role == USER_ROLE_DOCTOR)
User.thumb100 = property(lambda self: self.user_profile.thumb100)
User.thumb50 = property(lambda self: self.user_profile.thumb50)


AnonymousUser.is_regular = True
AnonymousUser.is_doctor = False
AnonymousUser.is_admin = False
AnonymousUser.is_author = False

AnonymousUser.image = None
AnonymousUser.email_confirmed = False
AnonymousUser.karm = 0
AnonymousUser.activity = 0