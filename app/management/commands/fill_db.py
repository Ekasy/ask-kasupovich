from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from app.models import *
from random import randint
from faker import *


class Command(BaseCommand):
    help = 'The command generates test data and populates the database with it'

    def add_arguments(self, parser):
        parser.add_argument('tags', type=int, help='Indicates the number of tags')
        parser.add_argument('users', type=int, help='Indicates the number of users')
        parser.add_argument('questions', type=int, help='Indicates the number of questions')
        parser.add_argument('answers', type=int, help='Indicates the maximum number of answers per question')

    def create_tags(self, fake, tags_num):
        for _ in range(tags_num):
            tag = Tag(tag=fake.word())
            tag.save()

    def create_users(self, fake, users_num):
        for _ in range(users_num):
            uname = fake.user_name()
            user = User(username=uname, password=fake.password(), email=fake.email())
            user.save()
            prfl = Profile(user=user, nickname=uname, avatar='../../../static/img/avatar.png')
            prfl.save()

    def create_questions(self, fake, questions_num):
        profile_id = Profile.objects.values_list('id', flat=True)
        tags_id = Tag.objects.values_list('id', flat=True)
        for _ in range(questions_num):
            question = Question(title=fake.sentence()[:20],
                                text=fake.text(),
                                profile=Profile.objects.get(pk=profile_id[randint(0, profile_id.count() - 1)]))
            question.save()

            tag_num = randint(0, 10)
            for _ in range(tag_num):
                question.tags.add(Tag.objects.get(pk=tags_id[randint(0, tags_id.count() - 1)]))
            question.save()

    def create_answers(self, fake, answers_num):
        profile_ids = Profile.objects.values_list('id', flat=True)
        question_ids = Question.objects.values_list('id', flat=True)
        profiles_num = profile_ids.count() - 1
        questions_num = question_ids.count() - 1
        for _ in range(questions_num):
            cur_answers_num = randint(0, answers_num)
            for _ in range(cur_answers_num):
                question_id = question_ids[randint(0, questions_num)]
                answer = Answer(text=fake.text(),
                                is_correct=False,
                                question=Question.objects.get(pk=question_id),
                                profile=Profile.objects.get(pk=profile_ids[randint(0, profiles_num)]))
                question = Question.objects.get(pk=question_id)
                question.answer_count += 1
                question.save()
                answer.save()

    def create_likes(self):
        questions = Question.objects.get_queryset()
        questions_num = questions.count()
        users = User.objects.get_queryset()
        users_num = users.count()
        for _ in range(users_num):
            for _ in range(questions_num):
                if randint(0, 1) == 1:
                    question_id = randint(1, questions_num)
                    try:
                        like = Like(content_object=Question.objects.get(pk=question_id),
                                    vote=1,
                                    user=User.objects.get(pk=randint(1, users_num)))
                        question = Question.objects.get(pk=question_id)
                        question.rating += 1
                        question.save()
                        like.save()
                    except IntegrityError:
                        pass

    def handle(self, *args, **options):
        fake = Faker()
        tags = options['tags']
        users = options['users']
        questions = options['questions']
        answers = options['answers']

        self.create_tags(fake, tags)
        self.create_users(fake, users)
        self.create_questions(fake, questions)
        self.create_answers(fake, answers)
        self.create_likes()
