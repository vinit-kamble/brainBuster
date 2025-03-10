from django.contrib import admin
from .models import Quiz, Question, Option, Participation

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'created_by', 'created_at')
    search_fields = ('title', 'code', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'time_limit')
    search_fields = ('text',)

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'submitted_at')
    search_fields = ('user__username', 'quiz__title')
