from math import asin, atan2, copysign, cos, degrees, fabs, pi
from pathlib import Path

import ezdxf
import numpy as np
from django.conf import settings
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.db import models
from ezdxf import colors
from ezdxf.addons import meshex
from ezdxf.math import Vec3
from ezdxf.render import MeshBuilder


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

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    def __str__(self):
        return self.title

    def check_material_file_name(self):
        # this function should be called only if
        # obj_model and mtl_model exist

        # get the material file name
        mtl_name = self.mtl_model.name.split("/")[-1]
        # get files for object file and helper file
        helper_path = Path(settings.MEDIA_ROOT).joinpath(
            "uploads/djaframe/scene/temp.obj"
        )
        obj_path = Path(self.obj_model.path)
        # copy helper from object file
        with open(obj_path, "r") as o_f, open(helper_path, "w") as h_f:
            for line in o_f:
                if line.startswith("mtllib"):
                    h_f.write(f"mtllib {mtl_name}\n")
                else:
                    h_f.write(line)
        # copy object file back
        with open(obj_path, "w") as o_f, open(helper_path, "r") as h_f:
            for line in h_f:
                o_f.write(line)


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
    dxf = models.FileField(
        "DXF file",
        help_text="Please, transform 3DSolids into Meshes before upload",
        max_length=200,
        upload_to="uploads/djaframe/scene/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "dxf",
                ]
            )
        ],
    )

    class Meta:
        verbose_name = "Scene"
        verbose_name_plural = "Scenes"

    def __str__(self):
        return self.title

    __original_dxf = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_dxf = self.dxf

    def save(self, *args, **kwargs):
        # save and eventually upload DXF
        super().save(*args, **kwargs)
        if self.__original_dxf != self.dxf:
            all_objects = self.staged_entities.all()
            if all_objects.exists():
                all_objects.delete()
            self.create_objs_from_dxf()

    def create_objs_from_dxf(self):
        doc = ezdxf.readfile(self.dxf.path)
        # make layer dict
        layer_dict = {}
        for layer in doc.layers:
            if layer.rgb:
                color = cad2hex(layer.rgb)
            else:
                color = cad2hex(layer.color)
            layer_dict[layer.dxf.name] = color
        # get model space
        msp = doc.modelspace()
        # prepare two helper files
        path = Path(settings.MEDIA_ROOT).joinpath("uploads/djaframe/scene/temp.obj")
        path2 = Path(settings.MEDIA_ROOT).joinpath("uploads/djaframe/scene/temp2.obj")
        # iterate over layers
        for name, color in layer_dict.items():
            # write first file recording vertex number
            with open(path, "w") as f:
                for m in msp.query(f"MESH[layer=='{name}']"):
                    mb = MeshBuilder()
                    mb.vertices = Vec3.list(m.vertices)
                    mb.faces = m.faces
                    f.write(meshex.obj_dumps(mb))
                    f.write(f"# total vertices={len(m.vertices)}\n")
            # pass values from one file to the other
            with open(path, "r") as f, open(path2, "w") as f2:
                # file is empty, pass
                if len(f.readlines()) == 0:
                    continue
                # rewind file!
                f.seek(0)
                f2.write("# Generated by django-a-frame\n")
                # offset face number by total vertex number
                n = 0
                for line in f:
                    if line.startswith("v"):
                        f2.write(line)
                    elif line.startswith("# total vertices="):
                        n += int(line.split("=")[1])
                    elif line.startswith("f"):
                        fc = line.split(" ")
                        f2.write(f"f {int(fc[1])+n} {int(fc[2])+n} {int(fc[3])+n}\n")
            with open(path2, "r") as f:
                entity = Entity.objects.create(
                    title=f"Layer {name}",
                    description="Generated by django-a-frame",
                    switch=True,
                )
                entity.obj_model = File(f, name="object.obj")
                entity.save()
                Staging.objects.create(
                    scene=self,
                    entity=entity,
                    color=color,
                    data={"Layer": name},
                )
        # iterate over blocks
        for block in doc.blocks:
            if block.name in [
                "*Model_Space",
            ]:
                continue
            # write first file recording vertex number
            with open(path, "w") as f:
                for m in block.query("MESH"):
                    mb = MeshBuilder()
                    mb.vertices = Vec3.list(m.vertices)
                    mb.faces = m.faces
                    f.write(meshex.obj_dumps(mb))
                    f.write(f"# total vertices={len(m.vertices)}\n")
            # pass values from one file to the other
            with open(path, "r") as f, open(path2, "w") as f2:
                # file is empty, pass
                if len(f.readlines()) == 0:
                    continue
                # rewind file!
                f.seek(0)
                f2.write("# Generated by django-a-frame\n")
                # offset face number by total vertex number
                n = 0
                for line in f:
                    if line.startswith("v"):
                        f2.write(line)
                    elif line.startswith("# total vertices="):
                        n += int(line.split("=")[1])
                    elif line.startswith("f"):
                        fc = line.split(" ")
                        f2.write(f"f {int(fc[1])+n} {int(fc[2])+n} {int(fc[3])+n}\n")
            with open(path2, "r") as f:
                # we create the block entity
                entity = Entity.objects.create(
                    title=f"Block {block.name}",
                    description="Generated by django-a-frame",
                    switch=True,
                )
                entity.obj_model = File(f, name="object.obj")
                entity.save()
            # we look for insertions of the block
            for ins in msp.query(f"INSERT[name=='{block.name}']"):
                # extract attributes
                attrib_dict = {}
                if ins.attribs:
                    for attr in ins.attribs:
                        attrib_dict[attr.dxf.tag] = attr.dxf.text
                # for 3D rotated insertions we need origin of local coords
                origin = ins.ucs().origin
                # and vectors of local coords...
                R = np.asarray(
                    [list(ins.ucs().ux), list(ins.ucs().uy), list(ins.ucs().uz)]
                )
                # ...to extract 3D rotation of insertion
                yaw, roll, pitch, gimbal_lock = rotation_matrix_to_euler_angles_zyx(R)
                Staging.objects.create(
                    scene=self,
                    entity=entity,
                    color=layer_dict[ins.dxf.layer],
                    position=(f"{origin[0]} {origin[2]} {-origin[1]}"),
                    rotation=f"{degrees(-pitch)} {degrees(-yaw)} {degrees(roll)}",
                    scale=f"{ins.dxf.xscale} {ins.dxf.zscale} {ins.dxf.yscale}",
                    data={
                        "Block": block.name,
                        "Layer": ins.dxf.layer,
                        "attribs": attrib_dict,
                    },
                )


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
    color = models.CharField(default="#FFFFFF", max_length=7)
    data = models.JSONField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Staging"
        verbose_name_plural = "Stagings"

    def __str__(self):
        return f"Staging {self.id}"

    def popupContent(self):
        if not self.data:
            return
        else:
            out = ""
            for key, value in self.data.items():
                if key == "attribs":
                    out += "Attributes:\n"
                    for t, v in value.items():
                        out += f"--{t}: {v}\n"
                else:
                    out += f"{key}: {value}\n"
            return out


"""
    Collection of utilities
"""


def cad2hex(color):
    if isinstance(color, tuple):
        return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
    rgb24 = colors.DXF_DEFAULT_COLORS[color]
    return "#{:06X}".format(rgb24)


# This is the floating point error tolerance.
EPSILON = 1e-6


def rotation_matrix_to_euler_angles_zyx(R):
    """
    From https://github.com/duolu/pyrotation

    Converting a rotation matrix representation to
    a rotation represented by three Euler angles (z-y'-x").

    CAUTION: Euler angles have a singularity when pitch = pi / 2 or - pi / 2,
    i.e., gimbal lock. In this case, yaw and roll angles can not be determined
    uniquely, and this function always return a zero yaw angle.

    """
    if fabs(fabs(R[2, 0]) - 1) < EPSILON:
        # cos(y) != 0, gimbal lock
        # CAUTION: y is always pi/2, and z is always 0
        y = copysign(pi / 2, -R[2, 0])
        x = 0
        z = atan2(R[0, 1], R[0, 2])
        gimbal_lock = True
        # print('gimbal lock!!!')
    else:
        # cos(y) == 0, normal situation
        # CAUTION: y is always in [-pi/2, pi/2]
        y = -asin(R[2, 0])
        cy = cos(y)
        x = atan2(R[2, 1] / cy, R[2, 2] / cy)
        z = atan2(R[1, 0] / cy, R[0, 0] / cy)
        gimbal_lock = False
    return z, y, x, gimbal_lock
