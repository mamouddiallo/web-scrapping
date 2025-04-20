# base/models/helpers.py

from django.db import models

class NamedDateTimeModel(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Ce modèle ne sera pas créé directement dans la base de données
