from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='quiz_dashboard'),
    path('create/', views.create_quiz, name='create_quiz'),
    path('join/', views.join_quiz, name='join_quiz'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:quiz_id>/', views.create_quiz, name='edit_quiz'),
    path('delete/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/play/', views.play_quiz, name='play_quiz'),
    path('quiz/<int:quiz_id>/results/<int:participation_id>/', views.quiz_results, name='quiz_results'),
    path('quiz/<int:quiz_id>/stats/', views.quiz_stats, name='quiz_stats'),
]
