from django.contrib import admin
from . import models


class PostAdminMixin(admin.ModelAdmin):
    readonly_fields = ['post_type']


@admin.register(models.Drug)
class DrugAdmin(PostAdminMixin):
    pass



@admin.register(models.DrugDosageForm)
class DrugDosageFormAdmin(PostAdminMixin):
    pass


@admin.register(models.DrugUsageArea)
class DrugUsageAreaAdmin(PostAdminMixin):
    pass


@admin.register(models.Component)
class ComponentAdmin(PostAdminMixin):
    pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Post)
class PostAdmin(PostAdminMixin):
    pass

@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Brand)
class BrandAdmin(PostAdminMixin):
    pass


@admin.register(models.CosmeticsUsageArea)
class CosmeticsUsageAreaAdmin(PostAdminMixin):
    pass

@admin.register(models.CosmeticsDosageForm)
class CosmeticsDosageFormAdmin(PostAdminMixin):
    pass


@admin.register(models.CosmeticsLine)
class CosmeticsLineAdmin(PostAdminMixin):
    pass

from mptt.admin import MPTTModelAdmin
@admin.register(models.Category)
class CategoryAdmin(MPTTModelAdmin, PostAdmin):
    pass
