from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext as _


def create_djaframe_group(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    grp, created = Group.objects.get_or_create(name=_("3D Manager"))
    if created:
        types = ContentType.objects.filter(app_label="djaframe").values_list(
            "id", flat=True
        )
        permissions = Permission.objects.filter(content_type_id__in=types)
        grp.permissions.set(permissions)


class DjaframeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djaframe"

    def ready(self):

        post_migrate.connect(create_djaframe_group, sender=self)
