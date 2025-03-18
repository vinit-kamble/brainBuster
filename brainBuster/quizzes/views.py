from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.urls import reverse
import json
from .models import Quiz, Question, Option, Participation, Answer
from datetime import datetime
from django.utils import timezone

@login_required
def dashboard(request):
    """Display the user's dashboard with created and participated quizzes."""
    created_quizzes = Quiz.objects.filter(created_by=request.user)
    all_participated_quizzes = request.user.participations.all().select_related('quiz')
    
    # Filter to most recent participation per quiz for "Your Activity" and stats
    unique_quizzes = {}
    for participation in all_participated_quizzes:
        quiz_id = participation.quiz.id
        if quiz_id not in unique_quizzes:
            unique_quizzes[quiz_id] = participation
    participated_quizzes = list(unique_quizzes.values())
    
    # Calculate average score for participated quizzes (based on unique quizzes)
    total_score = sum(p.score for p in participated_quizzes if p.score is not None)
    total_quizzes = len(participated_quizzes)
    average_score = round(total_score / total_quizzes, 1) if total_quizzes > 0 else 0
    
    # Calculate metrics for each created quiz using only the most recent participation per user
    for quiz in created_quizzes:
        all_participations = list(quiz.participations.all().select_related('user').order_by('user__id', '-submitted_at'))
        
        # Filter to most recent participation per user
        unique_users = {}
        for participation in all_participations:
            user_id = participation.user.id
            if user_id not in unique_users:
                unique_users[user_id] = participation
        
        participations = list(unique_users.values())
        quiz.total_participants = len(participations)
        if quiz.total_participants > 0:
            quiz.avg_score = round(sum(p.score for p in participations) / quiz.total_participants, 1)
            passing_participants = sum(1 for p in participations if p.score >= quiz.minimum_score_percentage)
            quiz.pass_rate = round((passing_participants / quiz.total_participants) * 100, 1)
            total_time = sum(p.total_time_taken for p in participations if p.total_time_taken is not None)
            quiz.avg_time = round(total_time / quiz.total_participants, 1)
        else:
            quiz.avg_score = 0
            quiz.pass_rate = 0
            quiz.avg_time = 0
    
    return render(request, 'quizzes/dashboard.html', {
        'created_quizzes': created_quizzes,
        'participated_quizzes': participated_quizzes,
        'average_score': average_score,
        'total_quizzes': total_quizzes,
    })

@login_required
def create_quiz(request, quiz_id=None):
    """Create or edit a quiz."""
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
            
            if is_editing:
                quiz.title = title
                quiz.description = description
                quiz.icon = icon
                quiz.time_limit_per_question = time_limit
                quiz.save()
                
                for question in Question.objects.filter(quiz=quiz):
                    Option.objects.filter(question=question).delete()
                Question.objects.filter(quiz=quiz).delete()
                
                messages.success(request, 'Quiz updated successfully!')
            else:
                quiz = Quiz.objects.create(
                    title=title,
                    description=description,
                    icon=icon,
                    time_limit_per_question=time_limit,
                    created_by=request.user
                )
                messages.success(request, 'Quiz created successfully!')

            for q_data in quiz_data['questions']:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['text']
                )
                
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

    context = {'is_editing': is_editing}
    questions_data = []

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
    """Delete a quiz created by the user."""
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('dashboard')
    
    return HttpResponseNotAllowed(['POST'])

def join_quiz(request):
    """Join a quiz using a code."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        
        if not code:
            messages.error(request, 'Please enter a quiz code.')
            return render(request, 'quizzes/join_quiz.html')

        try:
            quiz = Quiz.objects.get(code=code)
            
            if request.user.is_authenticated:
                if not quiz.participations.filter(user=request.user).exists():
                    messages.success(request, f'Joined quiz: {quiz.title}')
                else:
                    messages.info(request, f'You have already joined this quiz: {quiz.title}')

            return redirect('play_quiz', quiz_id=quiz.id)
        
        except Quiz.DoesNotExist:
            messages.error(request, 'Quiz not found with that code.')

    return render(request, 'quizzes/join_quiz.html')

def play_quiz(request, quiz_id):
    """Play a quiz and submit answers."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.user.is_authenticated:
        is_creator = quiz.created_by == request.user
        is_participant = quiz.participations.filter(user=request.user).exists()
    else:
        is_creator = False
        is_participant = False
    
    if request.method == 'POST':
        try:
            user_answers = json.loads(request.POST.get('answers', '{}'))
            total_time_taken = int(request.POST.get('totalTimeTaken', 0))
            
            score = 0
            total_questions = quiz.questions.count()
            
            if request.user.is_authenticated:
                # Calculate the next attempt number
                previous_attempts = Participation.objects.filter(user=request.user, quiz=quiz).count()
                attempt_number = previous_attempts + 1
                
                # Create a new participation for this attempt
                participation = Participation.objects.create(
                    user=request.user,
                    quiz=quiz,
                    score=0,  # Will update after calculation
                    total_time_taken=total_time_taken,
                    submitted_at=timezone.now(),
                    attempt_number=attempt_number
                )
                
                for question_id, answer_data in user_answers.items():
                    question = Question.objects.get(id=question_id)
                    option_id = answer_data.get('optionId')
                    time_taken = answer_data.get('timeTaken', 0)
                    
                    selected_option = Option.objects.get(id=option_id) if option_id else None
                    is_correct = selected_option.is_correct if selected_option else False
                    if is_correct:
                        score += 1
                    
                    Answer.objects.create(
                        participation=participation,
                        question=question,
                        selected_option=selected_option,
                        time_taken=time_taken
                    )
                
                percentage_score = (score / total_questions * 100) if total_questions > 0 else 0
                participation.score = percentage_score
                participation.save()
                
                return redirect('quiz_results', quiz_id=quiz.id, participation_id=participation.id)
            else:
                # Anonymous users: Calculate score and store in session
                answers_data = {}
                for question_id, answer_data in user_answers.items():
                    question = Question.objects.get(id=question_id)
                    option_id = answer_data.get('optionId')
                    time_taken = answer_data.get('timeTaken', 0)
                    
                    selected_option = Option.objects.get(id=option_id) if option_id else None
                    is_correct = selected_option.is_correct if selected_option else False
                    if is_correct:
                        score += 1
                    
                    answers_data[question_id] = {
                        'option_id': option_id,
                        'time_taken': time_taken
                    }
                
                percentage_score = (score / total_questions * 100) if total_questions > 0 else 0
                request.session['anonymous_quiz_result'] = {
                    'quiz_id': quiz.id,
                    'score': percentage_score,
                    'total_time_taken': total_time_taken,
                    'answers': answers_data,
                    'submitted_at': timezone.now().isoformat()
                }
                return redirect('quiz_results', quiz_id=quiz.id, participation_id=0)
            
        except json.JSONDecodeError:
            messages.error(request, 'There was an error processing your answers.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    questions = list(quiz.questions.prefetch_related('options').all())
    
    return render(request, 'quizzes/play_quiz.html', {
        'quiz': quiz,
        'questions': questions,
        'is_creator': is_creator
    })

def quiz_results(request, quiz_id, participation_id):
    """Display quiz results for a participation."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if participation_id == 0:
        anonymous_result = request.session.get('anonymous_quiz_result', {})
        if str(anonymous_result.get('quiz_id')) != str(quiz_id):
            messages.error(request, 'Quiz results not found.')
            return redirect('home')
        
        class AnonymousParticipation:
            def __init__(self, data):
                self.score = data.get('score', 0)
                self.total_time_taken = data.get('total_time_taken', 0)
                self.submitted_at = datetime.fromisoformat(data.get('submitted_at', timezone.now().isoformat()))
                self.is_anonymous = True
        
        participation = AnonymousParticipation(anonymous_result)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        participation = get_object_or_404(Participation, id=participation_id, user=request.user, quiz=quiz)
        participation.is_anonymous = False
    
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

@login_required
def quiz_stats(request, quiz_id):
    """Display detailed statistics for a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    # Get all participations, ordered by user and submission time (latest first)
    all_participations = list(quiz.participations.all().select_related('user').order_by('user__id', '-submitted_at'))
    
    # Filter to most recent participation per user
    unique_users = {}
    for participation in all_participations:
        user_id = participation.user.id
        if user_id not in unique_users:
            unique_users[user_id] = participation
    
    # List of most recent participations
    participations = list(unique_users.values())
    
    # Calculate total attempts per user for display
    user_attempts = {}
    for participation in all_participations:
        user_id = participation.user.id
        user_attempts[user_id] = user_attempts.get(user_id, 0) + 1
    for participation in participations:
        participation.attempts = user_attempts[participation.user.id]
    
    total_participants = len(participations)
    average_score = 0
    pass_rate = 0
    average_time = 0
    average_attempts = 0
    
    if total_participants > 0:
        average_score = sum(p.score for p in participations) / total_participants
        passing_participants = sum(1 for p in participations if p.score >= quiz.minimum_score_percentage)
        pass_rate = (passing_participants / total_participants * 100)
        total_time = sum(p.total_time_taken for p in participations if p.total_time_taken is not None)
        average_time = total_time / total_participants if total_participants > 0 else 0
        average_attempts = sum(user_attempts.values()) / len(user_attempts) if user_attempts else 0
    
    questions = list(quiz.questions.all().prefetch_related('options'))
    for question in questions:
        answers = Answer.objects.filter(question=question, participation__in=participations)
        total_answers = answers.count()
        
        if total_answers > 0:
            correct_count = answers.filter(selected_option__is_correct=True).count()
            question.correct_rate = round((correct_count / total_answers * 100), 1)
            total_time = sum(a.time_taken for a in answers if a.time_taken is not None)
            question.avg_time = round(total_time / total_answers, 1)
            
            if question.correct_rate >= 70:
                question.difficulty = "Easy"
                question.difficulty_class = "bg-success"
            elif question.correct_rate >= 40:
                question.difficulty = "Medium"
                question.difficulty_class = "bg-warning"
            else:
                question.difficulty = "Hard"
                question.difficulty_class = "bg-danger"
        else:
            question.correct_rate = 0
            question.avg_time = 0
            question.difficulty = "N/A"
            question.difficulty_class = "bg-secondary"
    
    return render(request, 'quizzes/quiz_stats.html', {
        'quiz': quiz,
        'participations': participations,  # Only latest per user
        'all_participations': all_participations,  # For modal
        'average_score': average_score,
        'pass_rate': pass_rate,
        'average_time': average_time,
        'average_attempts': average_attempts,
        'questions': questions,
    })

@login_required
def save_anonymous_result(request):
    """Save anonymous quiz result to the user's account after login/signup."""
    anonymous_result = request.session.get('anonymous_quiz_result')
    if not anonymous_result or str(anonymous_result.get('quiz_id')) not in [str(q.id) for q in Quiz.objects.all()]:
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=anonymous_result['quiz_id'])
    
    # Calculate attempt number
    previous_attempts = Participation.objects.filter(user=request.user, quiz=quiz).count()
    attempt_number = previous_attempts + 1
    
    # Create participation
    participation = Participation.objects.create(
        user=request.user,
        quiz=quiz,
        score=anonymous_result['score'],
        total_time_taken=anonymous_result['total_time_taken'],
        submitted_at=datetime.fromisoformat(anonymous_result['submitted_at']),
        attempt_number=attempt_number
    )
    
    # Save answers
    for question_id, answer_data in anonymous_result['answers'].items():
        question = Question.objects.get(id=question_id)
        option_id = answer_data['option_id']
        time_taken = answer_data['time_taken']
        
        selected_option = Option.objects.get(id=option_id) if option_id else None
        Answer.objects.create(
            participation=participation,
            question=question,
            selected_option=selected_option,
            time_taken=time_taken
        )
    
    # Clear session data
    del request.session['anonymous_quiz_result']
    messages.success(request, 'Your quiz result has been saved to your account!')
    return redirect('quiz_results', quiz_id=quiz.id, participation_id=participation.id)