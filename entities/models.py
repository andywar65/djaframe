from django.core.validators import FileExtensionValidator
from django.db import models


class Entity(models.Model):

    obj_model = models.FileField(
        "OBJ file",
        max_length=200,
        upload_to="uploads/aframe/obj/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "obj",
                ]
            )
        ],
    )
    mtl_model = models.FileField(
        "MTL file",
        max_length=200,
        upload_to="uploads/aframe/obj/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "mtl",
                ]
            )
        ],
    )

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
