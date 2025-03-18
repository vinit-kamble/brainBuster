from django.contrib import admin
from .models import Quiz, Question, Option, Participation, Answer

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz']
    inlines = [OptionInline]
    search_fields = ['text', 'quiz__title']

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'code']
    search_fields = ['title', 'description', 'code']
    list_filter = ['created_at']
    inlines = [QuestionInline]

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['user__username', 'quiz__title']

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Answer)