from django.core.validators import FileExtensionValidator
from django.db import models


class Entity(models.Model):

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
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
        null=True,
        blank=True,
    )
    switch = models.BooleanField(default=False, help_text="Switch Z/Y axis")

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"

    def __str__(self):
        return self.title
