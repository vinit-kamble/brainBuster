# quizzes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.urls import reverse
import json
from .models import Quiz, Question, Option, Participation
from datetime import datetime

@login_required
def dashboard(request):
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    participated_quizzes = request.user.participations.all().select_related('quiz')
    
    # Calculate average score
    total_score = sum(p.score for p in participated_quizzes if p.score is not None)
    total_quizzes = participated_quizzes.count()
    average_score = round(total_score / total_quizzes) if total_quizzes > 0 else 0
    
    return render(request, 'quizzes/dashboard.html', {
        'created_quizzes': created_quizzes,
        'participated_quizzes': participated_quizzes,
        'average_score': average_score,  # Pass it to the template
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

# Remove @login_required decorator
def join_quiz(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        
        if not code:
            messages.error(request, 'Please enter a quiz code.')
            return render(request, 'quizzes/join_quiz.html')

        try:
            quiz = Quiz.objects.get(code=code)
            
            # For logged in users, check participation
            if request.user.is_authenticated:
                if quiz.participations.filter(user=request.user).exists():
                    messages.info(request, f'You have already joined this quiz: {quiz.title}')
                else:
                    quiz.participations.create(user=request.user)
                    messages.success(request, f'Joined quiz: {quiz.title}')

            return redirect('play_quiz', quiz_id=quiz.id)
        
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found with that code.')

    return render(request, 'quizzes/join_quiz.html')


# Remove @login_required decorator
def play_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # For logged in users
    if request.user.is_authenticated:
        # Check if user is creator or has joined the quiz
        is_creator = quiz.created_by == request.user
        is_participant = quiz.participations.filter(user=request.user).exists()
        
        # If user hasn't joined and isn't the creator, add them as a participant
        if not is_participant and not is_creator:
            quiz.participations.create(user=request.user)
            is_participant = True
            messages.success(request, f'You have joined: {quiz.title}')
    else:
        # For anonymous users
        is_creator = False
        is_participant = False  # Anonymous users don't have participation records
    
    # Handle quiz submission
    if request.method == 'POST':
        try:
            user_answers = json.loads(request.POST.get('answers', '{}'))
            time_taken = int(request.POST.get('timeTaken', 0))
            
            # Calculate score
            score = 0
            total_questions = quiz.questions.count()
            answered_questions = 0
            
            # Process each question and calculate score
            for question in quiz.questions.all().prefetch_related('options'):
                question_id = str(question.id)
                
                if question_id in user_answers:
                    answered_questions += 1
                    user_option_id = user_answers[question_id].get('optionId')
                    
                    # Check if the selected option is correct
                    try:
                        selected_option = Option.objects.get(id=user_option_id)
                        if selected_option.is_correct:
                            score += 1
                    except Option.DoesNotExist:
                        pass
            
            # Calculate percentage score
            percentage_score = (score / total_questions) * 100 if total_questions > 0 else 0
            
            # For logged in users, update participation
            if request.user.is_authenticated:
                participation, created = Participation.objects.update_or_create(
                    user=request.user,
                    quiz=quiz,
                    defaults={
                        'score': percentage_score,
                        'time_taken': time_taken
                    }
                )
                return redirect('quiz_results', quiz_id=quiz.id, participation_id=participation.id)
            else:
                # For anonymous users, store in session
                request.session['anonymous_quiz_result'] = {
                    'quiz_id': quiz.id,
                    'score': percentage_score,
                    'time_taken': time_taken,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                return redirect('quiz_results', quiz_id=quiz.id, participation_id=0)  # Use 0 for anonymous users
            
        except json.JSONDecodeError:
            messages.error(request, 'There was an error processing your answers.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    # Get all questions with their options for the quiz
    questions = list(quiz.questions.prefetch_related('options').all())
    
    return render(request, 'quizzes/play_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'is_creator': is_creator
    })
    

def quiz_results(request, quiz_id, participation_id):
    """View for showing quiz results after completion"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if anonymous (participation_id = 0)
    if participation_id == 0:
        # Get anonymous results from session
        anonymous_result = request.session.get('anonymous_quiz_result', {})
        
        # Verify it's for the correct quiz
        if str(anonymous_result.get('quiz_id')) != str(quiz_id):
            messages.error(request, 'Quiz results not found.')
            return redirect('home')
        
        # Create a temporary "participation" object
        class AnonymousParticipation:
            def __init__(self, data):
                self.score = data.get('score', 0)
                self.time_taken = data.get('time_taken', 0)
                self.submitted_at = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')
                self.is_anonymous = True
        
        participation = AnonymousParticipation(anonymous_result)
        
    else:
        # For authenticated users
        if not request.user.is_authenticated:
            return redirect('login')
        
        participation = get_object_or_404(Participation, id=participation_id, user=request.user, quiz=quiz)
        participation.is_anonymous = False
    
    # Get all questions with their options for the quiz
    questions = quiz.questions.prefetch_related('options').all()
    
    return render(request, 'quizzes/quiz_results.html', {
        'quiz': quiz,
        'participation': participation,
        'questions': questions,
        'score_percentage': participation.score,
        'correct_answers': int((participation.score / 100) * questions.count()),
        'total_questions': questions.count(),
        'is_anonymous': getattr(participation, 'is_anonymous', False)
    })