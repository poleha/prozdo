from django.contrib import admin
from . import models


@admin.register(models.Drug)
class DrugAdmin(admin.ModelAdmin):
    pass



@admin.register(models.DrugDosageForm)
class DrugDosageFormAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DrugUsageArea)
class DrugUsageAreaAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Component)
class ComponentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    pass
