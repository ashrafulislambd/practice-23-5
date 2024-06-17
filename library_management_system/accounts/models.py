from django.db import models
from django.contrib.auth.models import User

class UserVault(models.Model):
    user = models.OneToOneField(User, related_name="vault", on_delete=models.CASCADE)
    balance = models.IntegerField()
