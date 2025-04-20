from django.utils import timezone
from django.db import models


class ProduitKilimall(models.Model):
    titre = models.CharField(max_length=255)
    prix = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    product_url = models.URLField(max_length=500, null=True, blank=True)
    date_ajout = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.titre
