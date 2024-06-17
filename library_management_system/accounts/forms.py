from typing import Any
from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserVault

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit = False)
        if commit == True:
            user.save()
            vault = UserVault.objects.create(
                user = user,
                balance = 0,
            )
        return user
