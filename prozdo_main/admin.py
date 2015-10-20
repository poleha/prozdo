from django.contrib import admin
from . import models
from mptt.admin import MPTTModelAdmin
from sorl.thumbnail.admin import AdminImageMixin
import reversion

class PostAdminMixin(reversion.VersionAdmin):
    readonly_fields = ['post_type']


@admin.register(models.Drug)
class DrugAdmin(AdminImageMixin, PostAdminMixin):
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
class CommentAdmin(reversion.VersionAdmin):
    pass

@admin.register(models.Post)
class PostAdmin(PostAdminMixin):
    pass

@admin.register(models.History)
class HistoryAdmin(reversion.VersionAdmin):
    pass


@admin.register(models.UserProfile)
class UserProfileAdmin(AdminImageMixin, reversion.VersionAdmin):
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


@admin.register(models.Category)
class CategoryAdmin(MPTTModelAdmin, PostAdmin):
    pass


@admin.register(models.Cosmetics)
class CosmeticsAdmin(AdminImageMixin, PostAdmin):
    pass

@admin.register(models.Blog)
class BlogAdmin(AdminImageMixin, PostAdmin):
    pass

@admin.register(models.Mail)
class MailAdmin(reversion.VersionAdmin):
    pass