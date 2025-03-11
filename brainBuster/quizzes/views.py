from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import Quiz, Question, Option

@login_required
def dashboard(request):
    # Fetch quizzes created by and participated in by the user.
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    participated_quizzes = request.user.participations.all().select_related('quiz')
    
    return render(request, 'quizzes/dashboard.html', {
        'created_quizzes': created_quizzes,
        'participated_quizzes': participated_quizzes,
    })

@login_required
def create_quiz(request):
    if request.method == 'POST':
        # Extract form data
        title = request.POST.get('quiz_title')
        description = request.POST.get('quiz_description', '')
        icon = request.POST.get('quiz_icon', 'question-circle')
        time_limit = request.POST.get('time_limit_seconds', 30)
        quiz_data_json = request.POST.get('quiz_data')
        
        if not title:
            messages.error(request, 'Quiz title is required.')
            return render(request, 'quizzes/create_quiz.html')
        
        try:
            quiz_data = json.loads(quiz_data_json)
            
            # Create the quiz
            quiz = Quiz.objects.create(
                title=title,
                description=description,
                icon=icon,
                time_limit_per_question=time_limit,
                created_by=request.user
            )
            
            # Process questions
            for q_data in quiz_data['questions']:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['text']
                )
                
                # Process options
                for i, option_text in enumerate(q_data['options']):
                    Option.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=(i == q_data['correctAnswer'])
                    )
            
            messages.success(request, 'Quiz created successfully!')
            return redirect('dashboard')
        
        except json.JSONDecodeError:
            messages.error(request, 'Invalid quiz data format.')
        except Exception as e:
            messages.error(request, f'Error creating quiz: {str(e)}')
    
    return render(request, 'quizzes/create_quiz.html')

@login_required
def join_quiz(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        
        if not code:
            messages.error(request, 'Please enter a quiz code.')
            return render(request, 'quizzes/join_quiz.html')
        
        try:
            quiz = Quiz.objects.get(code=code)
            
            # Check if user already participated
            if quiz.participations.filter(user=request.user).exists():
                messages.info(request, f'You have already joined this quiz: {quiz.title}')
            else:
                # Create participation entry
                quiz.participations.create(user=request.user)
                messages.success(request, f'Joined quiz: {quiz.title}')
            
            return redirect('dashboard')
        
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found with that code.')
    
    return render(request, 'quizzes/join_quiz.html')

@login_required
def view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if user is the creator or a participant
    is_creator = quiz.created_by == request.user
    is_participant = quiz.participations.filter(user=request.user).exists()
    
    if not (is_creator or is_participant):
        messages.error(request, 'You do not have access to this quiz.')
        return redirect('dashboard')
    
    context = {
        'quiz': quiz,
        'is_creator': is_creator,
        'questions': quiz.questions.all().prefetch_related('options')
    }
    
    return render(request, 'quizzes/view_quiz.html', context)