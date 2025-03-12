# quizzes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.urls import reverse
import json
from .models import Quiz, Question, Option

@login_required
def dashboard(request):
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    participated_quizzes = request.user.participations.all().select_related('quiz')
    return render(request, 'quizzes/dashboard.html', {
        'created_quizzes': created_quizzes,
        'participated_quizzes': participated_quizzes,
    })

@login_required
def create_quiz(request, quiz_id=None):
    quiz = None
    is_editing = False
    
    if quiz_id:
        quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
        is_editing = True

    if request.method == 'POST':
        title = request.POST.get('quiz_title')
        description = request.POST.get('quiz_description', '')
        icon = request.POST.get('quiz_icon', 'question-circle')
        time_limit = request.POST.get('time_limit_seconds', 30)
        quiz_data_json = request.POST.get('quiz_data')
        
        if not title:
            messages.error(request, 'Quiz title is required.')
            return render(request, 'quizzes/create_quiz.html', {'quiz': quiz, 'is_editing': is_editing})

        try:
            quiz_data = json.loads(quiz_data_json)
            
            # In views.py, modify the question updating logic in create_quiz:
            # In the POST handling section of create_quiz view
            if is_editing:
                # Update existing quiz
                quiz.title = title
                quiz.description = description
                quiz.icon = icon
                quiz.time_limit_per_question = time_limit
                quiz.save()
                
                # Make sure to delete all existing questions AND their options
                for question in Question.objects.filter(quiz=quiz):
                    Option.objects.filter(question=question).delete()
                Question.objects.filter(quiz=quiz).delete()
                
                messages.success(request, 'Quiz updated successfully!')
            else:
                # Create new quiz
                quiz = Quiz.objects.create(
                    title=title,
                    description=description,
                    icon=icon,
                    time_limit_per_question=time_limit,
                    created_by=request.user
                )
                messages.success(request, 'Quiz created successfully!')

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

            return redirect('dashboard')

        except json.JSONDecodeError:
            messages.error(request, 'Invalid quiz data format.')
        except Exception as e:
            messages.error(request, f'Error {"updating" if is_editing else "creating"} quiz: {str(e)}')

    # Prepare context for GET request or form re-render
    # In views.py, in the create_quiz function

    # Modify the context preparation section:
    # Prepare context for GET request or form re-render
    context = {'is_editing': is_editing}

    questions_data = []  # Initialize this variable outside the if block

    if quiz:
        for question in quiz.questions.all().prefetch_related('options'):
            options = list(question.options.all())
            correct_index = next((i for i, opt in enumerate(options) if opt.is_correct), 0)
            questions_data.append({
                'text': question.text,
                'options': [opt.text for opt in options],
                'correctAnswer': correct_index
            })
        
        context.update({
            'quiz': quiz,
            'questions_data': json.dumps(questions_data)
        })

    return render(request, 'quizzes/create_quiz.html', context)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('dashboard')
    
    return HttpResponseNotAllowed(['POST'])

@login_required
def join_quiz(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        
        if not code:
            messages.error(request, 'Please enter a quiz code.')
            return render(request, 'quizzes/join_quiz.html')
        
        try:
            quiz = Quiz.objects.get(code=code)
            
            if quiz.participations.filter(user=request.user).exists():
                messages.info(request, f'You have already joined this quiz: {quiz.title}')
            else:
                quiz.participations.create(user=request.user)
                messages.success(request, f'Joined quiz: {quiz.title}')
            
            return redirect('dashboard')
        
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found with that code.')
    
    return render(request, 'quizzes/join_quiz.html')

@login_required
def view_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    is_creator = quiz.created_by == request.user
    is_participant = quiz.participations.filter(user=request.user).exists()
    
    if not (is_creator or is_participant):
        messages.error(request, 'You do not have access to this quiz.')
        return redirect('dashboard')
    
    return render(request, 'quizzes/view_quiz.html', {
        'quiz': quiz,
        'is_creator': is_creator,
        'questions': quiz.questions.all().prefetch_related('options')
    })