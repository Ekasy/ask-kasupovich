from django.shortcuts import render
from django.core.paginator import Paginator
from app.models import *

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


def new_question(request):
    return render(request, 'ask.html', {'popular_tags': popular_tags, 'best_members': best_members, })


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
    return render(request, 'question.html', {
        'question': question,
        'questions': paginate(answers, request, 3),
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def login(request):
    return render(request, 'login.html', {'popular_tags': popular_tags, 'best_members': best_members, })


def signup(request):
    return render(request, 'signup.html', {'popular_tags': popular_tags, 'best_members': best_members, })


def personal_page(request):
    personal_info = {
        "name": "Edin Kasupovich",
        "login": "ekasy",
        "nickname": "EKASY",
        "email": "ekasy@tech.com"
    }
    return render(request, 'personal_page.html', {
        "personal_info": personal_info,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })
