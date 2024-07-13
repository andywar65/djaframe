from pathlib import Path

from django.core.validators import FileExtensionValidator
from django.db import models


def entity_directory_path(instance, filename):
    return "uploads/djaframe/obj/{0}/{1}".format(instance.id, filename)


class Entity(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    obj_model = models.FileField(
        "OBJ file",
        max_length=200,
        upload_to=entity_directory_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "obj",
                ]
            )
        ],
        null=True,
    )
    mtl_model = models.FileField(
        "MTL file",
        max_length=200,
        upload_to=entity_directory_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "mtl",
                ]
            )
        ],
        null=True,
        blank=True,
    )
    switch = models.BooleanField(default=False, help_text="Switch Z/Y axis")
    color = models.CharField(default="#FFFFFF", max_length=7)

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    def __str__(self):
        return self.title


def material_image_directory_path(instance, filename):
    return "uploads/djaframe/obj/{0}/{1}".format(instance.entity.id, filename)


class MaterialImage(models.Model):
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="material_images",
        verbose_name="Material image",
    )
    image = models.ImageField(upload_to=material_image_directory_path)

    def __str__(self):
        return Path(self.image.url).name


class Scene(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "Scene"
        verbose_name_plural = "Scenes"

    def __str__(self):
        return self.title


class Staging(models.Model):
    scene = models.ForeignKey(
        Scene,
        on_delete=models.CASCADE,
        related_name="staged_entities",
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="scenes",
    )
    position = models.CharField(
        default="0 0 0",
        max_length=50,
        help_text="Left/Right - Up/Down - In/Out",
    )
    rotation = models.CharField(
        default="0 0 0",
        max_length=50,
        help_text="Pitch - Yaw - Roll",
    )
    scale = models.CharField(
        default="1 1 1",
        max_length=50,
        help_text="Width - Heigth - Depth",
    )
