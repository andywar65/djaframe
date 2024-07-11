from django.contrib import admin

from .models import Entity, Scene, Staging


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("title", "description")


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("title", "description")


@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ("id",)
