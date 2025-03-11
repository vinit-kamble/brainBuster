from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-start-0',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control border-start-0',
                'placeholder': 'Choose a unique username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control border-start-0',
                'placeholder': 'Create a secure password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control border-start-0',
                'placeholder': 'Confirm your password'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            UserProfile.objects.create(user=user)

        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control border-start-0',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control border-start-0',
            'placeholder': 'Enter your password'
        })
    )
