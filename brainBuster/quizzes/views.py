from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quiz
from .forms import QuizForm

@login_required
def dashboard(request):
    # Fetch quizzes created by and participated in by the user.
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    # Here you might also add logic for quizzes the user has joined.
    return render(request, 'quizzes/dashboard.html', {
        'created_quizzes': created_quizzes,
    })

@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            # Create a quiz instance without immediately saving it to add the creator
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('quiz_dashboard')
        else:
            # Form errors will be automatically passed to the template
            messages.error(request, 'There were errors in your submission.')
    else:
        form = QuizForm()
    return render(request, 'quizzes/create_quiz.html', {'form': form})

# @login_required
def join_quiz(request):
    if request.method == 'POST':
        # Logic to join a quiz using a code (not fully implemented here)
        code = request.POST.get('code')
        try:
            quiz = Quiz.objects.get(code=code)
            # Process participation logic here...
            messages.success(request, f'Joined quiz: {quiz.title}')
            return redirect('quiz_dashboard')
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found with that code.')
    return render(request, 'quizzes/join_quiz.html')
