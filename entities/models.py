from django.db import models


class Entity(models.Model):

    obj_model = models.FileField()

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
