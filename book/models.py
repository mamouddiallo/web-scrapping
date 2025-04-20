from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    stock = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField()
    image_local = models.ImageField(upload_to='book_images/')  # Pour stocker l'image localement
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # Note du livre entre 1 et 5
    
    def __str__(self):
        return self.title
