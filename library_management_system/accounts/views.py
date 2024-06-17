from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm

from borrowings.models import Transaction

class UserRegisterView(SuccessMessageMixin, CreateView):
    template_name = "accounts/signup.html"
    form_class = UserRegistrationForm
    success_message = "User account created successfully"
    success_url = reverse_lazy("index")

class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = "accounts/login.html"
    success_message = "Successfully Logged In"
    success_url = reverse_lazy("index")

@login_required
def profile(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, "accounts/profile.html", {
        "transactions": transactions,
    })

@login_required
def logout(request):
    logout(request)
    return redirect(reverse_lazy("index"))