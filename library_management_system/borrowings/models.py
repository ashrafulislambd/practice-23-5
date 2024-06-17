from django.db import models
from django.contrib.auth.models import User
from book.models import Book

from .constants import BORROW, RETURN, TRANSACTION_TYPE
from datetime import timezone
import datetime

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    mode = models.IntegerField(choices=TRANSACTION_TYPE)
    balance_after_transaction = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)