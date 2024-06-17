from django.db import models
from django.contrib.auth.models import User
from .constants import GENRE_CHOICES, REVIEW_CHOICES

class Book(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    image = models.ImageField(upload_to="media/books/")
    borrowing_price = models.IntegerField()
    category = models.CharField(max_length=100, choices=GENRE_CHOICES)

    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=REVIEW_CHOICES)
    review = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user',)