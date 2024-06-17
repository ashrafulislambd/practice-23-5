from typing import Any
from django import forms 
from django.contrib.auth.models import User

from .models import Review
from borrowings.models import Transaction

class DepositForm(forms.Form):
    amount = forms.IntegerField()

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be non-negative")
        return amount
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'review',)

    def __init__(self, *args, **kwargs):
        self.book = kwargs.pop('book')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.book = self.book
        self.instance.user = self.user
        print(dir(self.instance))
        return super().save()
    
    def clean(self):
        transaction_count = Transaction.objects.filter(book=self.book, user=self.user).count()
        if transaction_count == 0:
            raise forms.ValidationError("You must borrow this book to review on it")

        try:
            existing_review = Review.objects.get(book=self.book, user=self.user)
        except Review.DoesNotExist:
            existing_review = None
        if existing_review:
            raise forms.ValidationError("You cannot review more than one time.")