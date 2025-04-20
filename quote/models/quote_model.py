from django.db import models
from base.models.helpers import DateTimeModel
from quote.models.tag_model import TagModel


class QuoteModel(DateTimeModel):
    quote = models.TextField()
    text = models.TextField()
    tags = models.ManyToManyField(TagModel)
    author = models.CharField(max_length=40)