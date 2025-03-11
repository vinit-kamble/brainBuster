from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='quiz_dashboard'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('join/', views.join_quiz, name='join_quiz'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
