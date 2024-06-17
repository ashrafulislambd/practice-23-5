from django.urls import path   

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<int:book_id>', views.details, name='details'),
    path('deposit', views.deposit, name='deposit'),
    path('borrow', views.borrow, name='borrow'),
    path('return', views.return_book, name='return'),
]
