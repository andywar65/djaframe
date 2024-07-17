from pathlib import Path

import ezdxf
from django.core.validators import FileExtensionValidator
from django.db import models
from ezdxf import colors
from ezdxf.addons import meshex


def entity_directory_path(instance, filename):
    return "uploads/djaframe/obj/{0}/{1}".format(instance.id, filename)


class Entity(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    gltf_model = models.FileField(
        "GLTF file",
        help_text="Overrides all other entries",
        max_length=200,
        upload_to=entity_directory_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "gltf",
                    "glb",
                ]
            )
        ],
        null=True,
        blank=True,
    )
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
        blank=True,
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
    image = models.ImageField(
        upload_to="uploads/djaframe/scene/",
        null=True,
        blank=True,
        help_text="Equirectangular image",
    )

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


"""
    Collection of utilities
"""


def cad2hex(color):
    if isinstance(color, tuple):
        return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
    rgb24 = colors.DXF_DEFAULT_COLORS[color]
    return "#{:06X}".format(rgb24)


class DxfScene(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    dxf = models.FileField(
        "DXF file",
        help_text="Please, transform 3DSolids into Meshes before upload",
        max_length=200,
        upload_to="uploads/djaframe/dxf-scene/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "dxf",
                ]
            )
        ],
    )

    class Meta:
        verbose_name = "DXF Scene"
        verbose_name_plural = "DXF Scenes"

    __original_dxf = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_dxf = self.dxf

    def save(self, *args, **kwargs):
        # save and eventually upload DXF
        super().save(*args, **kwargs)
        if self.__original_dxf != self.dxf:
            all_objects = self.dxf_objects.all()
            if all_objects.exists():
                all_objects.delete()
            self.create_objs_from_dxf()

    def create_objs_from_dxf(self):
        doc = ezdxf.readfile(self.dxf.path)
        msp = doc.modelspace()  # noqa
        # prepare layer table
        layer_table = {}
        for layer in doc.layers:
            if layer.rgb:
                color = cad2hex(layer.rgb)
            else:
                color = cad2hex(layer.color)
            layer_table[layer.dxf.name] = {
                "color": color,
            }
        for m in msp.query("MESH"):
            obj = meshex.obj_dumps(m)
            print(obj)


class DxfObject(models.Model):
    scene = models.ForeignKey(
        DxfScene,
        on_delete=models.CASCADE,
        related_name="dxf_objects",
    )
    obj = models.FileField(
        max_length=200,
        upload_to=entity_directory_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "obj",
                ]
            )
        ],
    )
    color = models.CharField(default="#FFFFFF", max_length=7)
