from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
import json

from app.models import *
from app import forms

popular_tags = Tag.objects.get_best_tags()
best_members = Profile.objects.get_best_members()
objects_per_page = 5


def paginate(objects_list, request, per_page=objects_per_page):
    p = Paginator(objects_list, per_page)
    page = request.GET.get('page')
    objects_by_page = p.get_page(page)
    return objects_by_page


def index(request):
    new_qstns = Question.objects.get_new_questions()
    return render(request, 'index.html', {
        'questions': paginate(new_qstns, request),
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def hot_questions(request):
    hot_qstns = Question.objects.get_hot_questions()
    return render(request, 'hot_questions.html', {
        'questions': paginate(hot_qstns, request),
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


@login_required
def new_question(request):
    if request.method == 'GET':
        form = forms.QuestionForm(request.user)
        return render(request, 'ask.html', {'form': form, 'popular_tags': popular_tags, 'best_members': best_members, })

    form = forms.QuestionForm(request.user, request.POST)
    if form.is_valid():
        question = form.save()
        return redirect(reverse('one_question', kwargs={'pk': question.id, }))

    return render(request, 'ask.html', {'form': form, 'popular_tags': popular_tags, 'best_members': best_members, })


def questions_by_tag(request, tag_name):
    qstns_by_tag, tag = Question.objects.get_questions_by_tag(tag_name)
    return render(request, 'questions_by_tag.html', {
        "questions": paginate(qstns_by_tag, request),
        "tag": tag,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def one_question(request, pk):
    question, answers = Question.objects.get_one_question(pk)
    context = {'question': question, 'questions': paginate(answers, request, 3),
               'popular_tags': popular_tags, 'best_members': best_members, }
    if request.method == 'GET':
        form = forms.AnswerForm(request.user, question)
    else:
        form = forms.AnswerForm(request.user, question, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('one_question', kwargs={'pk': pk, }))

    context['form'] = form
    return render(request, 'question.html', context)


def login(request):
    if request.method == 'GET':
        form = forms.LoginForm()
    else:
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect('/?continue=%s' % request.path)
            else:
                form.add_error('password', 'Incorrect password')

    return render(request, 'login.html', {'form': form, 'popular_tags': popular_tags, 'best_members': best_members, })


def signup(request):
    if request.method == 'GET':
        form = forms.SignUpForm()
    else:
        form = forms.SignUpForm(data=request.POST)
        if form.is_valid():
            user, profile = form.save()
            auth.login(request, user)
            return redirect(reverse('new_questions'))

    return render(request, 'signup.html', {'form': form, 'popular_tags': popular_tags, 'best_members': best_members, })


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def settings(request):
    if request.method == 'GET':
        form = forms.SettingsForm(request.user)
    else:
        form = forms.SettingsForm(request.user, request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('settings'))
    return render(request, 'settings.html', {'form': form, 'popular_tags': popular_tags,
                                             'best_members': best_members, })


@login_required
@require_POST
def vote(request):
    form = forms.LikeForm(user=request.user, data=request.POST)
    if form.is_valid():
        rating = form.save()
        return JsonResponse({'rating':  rating})
    return JsonResponse({'rating':  0})


@login_required
@require_POST
def correct(request):
    form = forms.CorrectForm(data=request.POST)
    if form.is_valid():
        answer = form.save()
        return JsonResponse({'is_correct': answer.is_correct, })
    return JsonResponse({'is_correct': False, })

