from django import forms
from .models import Quiz

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'code', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional description'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique quiz code'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}),
        }
