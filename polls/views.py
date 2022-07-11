from bs4 import BeautifulSoup

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question, SecurityAnswer, Voter, Message


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]

    def get_context_data(self,**kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['latest_messages_list'] = Message.objects.order_by('-pub_date')[:5]
        return context


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


class AlreadyVotedView(generic.DetailView):
    model = Question
    template_name = 'polls/already_voted.html'


# FLAW 1: Unsafe vote function
@login_required
def vote_unsafe(request, question_id, user_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    user = get_object_or_404(User, pk=user_id)
    voters = Voter.objects.filter(user=user, question=question_id)
    if len(voters) > 1:
        # There shouldn't be more than one voter object for each user and question.
        return HttpResponseServerError()
    if len(voters) == 1 and voters[0].voted:
        return HttpResponseRedirect(reverse('polls:already_voted', args=(question.id,)))

    selected_choice.votes = F('votes') + 1
    selected_choice.save()
    if len(voters) == 1:
        voters[0].voted = True
        voters[0].save()
    else:
        voter = Voter(user=user, question=question, voted=True)
        voter.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

# FLAW 1: Safer vote function
@login_required
def vote_safe(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    voters = Voter.objects.filter(user=request.user, question=question_id)
    if len(voters) > 1:
        # There shouldn't be more than one voter object for each user and question.
        return HttpResponseServerError()
    if len(voters) == 1 and voters[0].voted:
        return HttpResponseRedirect(reverse('polls:already_voted', args=(question.id,)))

    selected_choice.votes = F('votes') + 1
    selected_choice.save()
    if len(voters) == 1:
        voters[0].voted = True
        voters[0].save()
    else:
        voter = Voter(user=request.user, question=question, voted=True)
        voter.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def add_message(request):
    # Use BeatifulSoup to message content to close any unclosed tags.
    content_str = str(BeautifulSoup(request.POST.get('content_text'), features='html.parser'))
    message = Message(heading_text=request.POST.get('heading_text'), content_text=content_str)
    message.save()
    return HttpResponseRedirect(reverse('polls:index'))

# FLAW 4: The whole design of the forgot password service is flawed and therefore functions
# forgot_my_password(), security_question() and change_password() should all be ditched and
# a more secure forgot my password service should be designed.
def forgot_my_password(request):
    return render(request, 'polls/forgot_my_password.html')

# FLAW 4: The whole design of the forgot password service is flawed and therefore functions
# forgot_my_password(), security_question() and change_password() should all be ditched and
# a more secure forgot my password service should be designed.
def security_question(request):
    username = request.POST.get('username')
    if not username:
        return render(request, 'polls/forgot_my_password.html', {
            'error_message': "You didn't provide a username.",
        })
    
    user = User.objects.filter(username=username)
    if not user:
        return render(request, 'polls/forgot_my_password.html', {
            'error_message': f"There is no user named '{username}'.",
        })

    security_answer_list = SecurityAnswer.objects.filter(user=user[0]).order_by('id')[:3]
    return render(request, 'polls/security_question.html', {
        'username': username,
        'security_answer_list': security_answer_list,
    })

# FLAW 4: The whole design of the forgot password service is flawed and therefore functions
# forgot_my_password(), security_question() and change_password() should all be ditched and
# a more secure forgot my password service should be designed.
def change_password(request):
    new_password_1 = request.POST.get('new_password_1')
    new_password_2 = request.POST.get('new_password_2')
    username = request.POST.get('username')
    users = User.objects.filter(username=username)

    if len(users) == 0:
        return HttpResponse(f"Error: User '{request.POST.get('username')}' not found.", status=404)
    user = users[0]

    security_answer_list = SecurityAnswer.objects.filter(user=user).order_by('id')[:3]

    for i, answer in enumerate(security_answer_list):
        answer_from_form = request.POST.get(f'answer{i+1}')

        if answer.answer_text != answer_from_form:
            return render(request, 'polls/security_question.html', {
                'username': username,
                'security_answer_list': security_answer_list,
                'error_message': 'Answer to one of the security questions was  wrong.',
            })

    if new_password_1 != new_password_2:
        return render(request, 'polls/security_question.html', {
            'username': username,
            'security_answer_list': security_answer_list,
            'error_message': 'Passwords do not match!',
        })

    user.password = make_password(new_password_1)
    user.save()
    login(request, user)
    return HttpResponseRedirect(reverse('polls:index'))
