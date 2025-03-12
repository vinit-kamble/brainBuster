from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='quiz_dashboard'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('join/', views.join_quiz, name='join_quiz'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('view/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
    path('edit/<int:quiz_id>/', views.create_quiz, name='edit_quiz'),
    path('delete/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
]
