from django.urls import path
from .import views

urlpatterns = [
    path('register', views.UserRegisterView.as_view() , name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('profile', views.profile, name='profile'),
    path('profile', views.logout, name='logout'),
]
