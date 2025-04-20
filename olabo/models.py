from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    availability = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField()
    image_local = models.ImageField(upload_to='olabo_images/')

    def __str__(self):
        return self.name
