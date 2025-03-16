import random
import string
from django.db import models
from django.contrib.auth.models import User


def generate_unique_code():
    length = 6
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Quiz.objects.filter(code=code).exists():
            return code

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default="question-circle")
    code = models.CharField(max_length=10, unique=True, default=generate_unique_code)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    created_at = models.DateTimeField(auto_now=True)
    time_limit_per_question = models.IntegerField(help_text="Time limit in seconds", default=30)
    minimum_score_percentage = models.IntegerField(help_text="Minimum score required to pass (%)", default=60)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    # Removed the time_limit as it will be defined at the quiz level

    def __str__(self):
        return f"Q: {self.text[:50]}..."  # Short preview of the question text


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='participations')
    score = models.FloatField(default=0.0)
    submitted_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add to auto_now
    time_taken = models.IntegerField(default=0, help_text="Total time taken in seconds")
    
    class Meta:
        unique_together = ('user', 'quiz')
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"