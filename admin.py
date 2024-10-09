from django.contrib import admin

from .models import Entity, MaterialImage, Scene, Staging


class MaterialImageInline(admin.TabularInline):
    model = MaterialImage
    extra = 0


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    inlines = [
        MaterialImageInline,
    ]
    actions = ["check_file_names"]

    @admin.action(description="Check material/image file names")
    def check_file_names(self, request, queryset):
        for ent in queryset:
            if ent.obj_model and ent.mtl_model:
                ent.check_material_file_name()


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ("title", "description")


@admin.register(Staging)
class StagingAdmin(admin.ModelAdmin):
    list_display = ("id", "scene", "entity")
