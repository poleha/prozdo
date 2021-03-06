from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from reversion.admin import VersionAdmin
from sorl.thumbnail.admin import AdminImageMixin

from super_model import models as super_models
from . import models


class PostAdminMixin(VersionAdmin):
    readonly_fields = ['post_type']


@admin.register(models.Drug)
class DrugAdmin(AdminImageMixin, PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias', 'body')


@admin.register(models.DrugDosageForm)
class DrugDosageFormAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.DrugUsageArea)
class DrugUsageAreaAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.Component)
class ComponentAdmin(PostAdminMixin):
    pass


@admin.register(models.Post)
class PostAdmin(PostAdminMixin):
    list_filter = ('status', 'post_type')
    search_fields = ('title', 'alias')


@admin.register(models.History)
class HistoryAdmin(VersionAdmin):
    list_filter = ('history_type',)


@admin.register(models.UserProfile)
class UserProfileAdmin(AdminImageMixin, VersionAdmin):
    list_filter = ('role',)
    search_fields = ('user__username',)


@admin.register(models.BrandModel)
class BrandAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.CosmeticsUsageArea)
class CosmeticsUsageAreaAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.CosmeticsDosageForm)
class CosmeticsDosageFormAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.CosmeticsLine)
class CosmeticsLineAdmin(PostAdminMixin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.Category)
class CategoryAdmin(MPTTModelAdmin, PostAdmin):
    list_filter = ('status',)
    search_fields = ('title', 'alias')


@admin.register(models.Cosmetics)
class CosmeticsAdmin(AdminImageMixin, PostAdmin):
    list_filter = ('status',)
    search_fields = ('title', 'alias', 'body')


@admin.register(models.Blog)
class BlogAdmin(AdminImageMixin, PostAdmin):
    list_filter = ('status',)
    search_fields = ('title', 'alias', 'body')


@admin.register(models.Mail)
class MailAdmin(VersionAdmin):
    list_filter = ('mail_type',)


def comment_mass_publish(CommentAdmin, request, queryset):
    queryset.update(status=super_models.COMMENT_STATUS_PUBLISHED)


comment_mass_publish.short_description = "Опубликовать выбранные сообщения"


def comment_mass_unpublish(CommentAdmin, request, queryset):
    queryset.update(status=super_models.COMMENT_STATUS_PENDING_APPROVAL)


comment_mass_unpublish.short_description = "Снять с публикации выбранные сообщения"


@admin.register(models.Comment)
class CommentAdmin(VersionAdmin):
    list_filter = ('status', 'consult_required', 'confirmed', 'delete_mark')
    search_fields = ('body',)
    actions = [comment_mass_publish, comment_mass_unpublish]
    readonly_fields = ('post_str', 'parent_str')
    exclude = ('post', 'parent')

    def parent_str(self, instance):
        return instance.parent.__str__()

    parent_str.short_description = 'Parent'

    def post_str(self, instance):
        return instance.post.__str__()

    post_str.short_description = 'Post'
