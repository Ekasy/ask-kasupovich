from django.shortcuts import render
from django.core.paginator import Paginator


tags = [
    {
        'id': idx,
        'name': f'tag{idx}',
    } for idx in range(2)
]


questions = [
    {
        'id': idx,
        'title': f'Title number {idx}',
        'text': f'Some text for question #{idx}',
        'tags': tags,
        'mark': 3,
        'answer_count': 4,
    } for idx in range(10)
]


popular_tags = [
    {'id': 1, 'name': 'python'}, {'id': 2, 'name': 'perl'}, {'id': 3, 'name': 'technopark'},
    {'id': 4, 'name': 'cpp'}, {'id': 5, 'name': 'mysql'}, {'id': 6, 'name': 'golang'},
]


best_members = ['Mr. Freedman', 'Dr. House', 'Queen Victoria', 'Ekasy']


def paginate(objects_list, request, per_page=3):
    p = Paginator(objects_list, per_page)
    page = request.GET.get('page')
    objects_by_page = p.get_page(page)
    return objects_by_page


def index(request):
    questions_by_page = paginate(questions, request)
    return render(request, 'index.html', {
        'questions': questions_by_page,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def hot_questions(request):
    questions_by_page = paginate(questions, request)
    return render(request, 'hot_questions.html', {
        'questions': questions_by_page,
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def new_question(request):
    return render(request, 'ask.html', {'popular_tags': popular_tags, 'best_members': best_members, })


def one_question(request, pk):
    question = questions[pk]
    comments = [
        {
            'id': idx,
            'text': f"It's probably a correct answer. Result is {idx}",
            'mark': 7,
        } for idx in range(4)
    ]

    comments_by_page = paginate(comments, request)

    return render(request, 'question.html', {
        "question": question,
        "questions": comments_by_page,  # важно! передаются комменты
        'popular_tags': popular_tags,
        'best_members': best_members,
    })


def questions_by_tag(request, name):
    que = paginate([questions[i] for i in range(len(name))], request)
    tag = {"id": len(name), "name": name}
    return render(request, 'questions_by_tag.html', {
        "questions": que,
        "tag": tag,
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
