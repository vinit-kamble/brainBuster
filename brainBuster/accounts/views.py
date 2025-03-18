from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, SignupForm
from django.contrib import messages

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('quiz_dashboard')

    def form_valid(self, form):
        """Handle successful login and check for anonymous quiz result."""
        response = super().form_valid(form)  # Logs in the user
        if 'anonymous_quiz_result' in self.request.session:
            return redirect('save_anonymous_result')  # Redirect to save the result
        return response

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Update terms_accepted if checkbox was checked
            terms_accepted = request.POST.get('terms', False) == 'on'
            if terms_accepted:
                user.profile.terms_accepted = True
                user.profile.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            # Check for anonymous result and save it
            if 'anonymous_quiz_result' in request.session:
                return redirect('save_anonymous_result')
            return redirect('quiz_dashboard')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')