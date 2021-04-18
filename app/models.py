from django.db import models
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey


class QuestionManager(models.Manager):
    def get_new_questions(self):
        return self.order_by('-id')

    def get_hot_questions(self):
        return self.order_by('-rating')

    def get_questions_by_tag(self, tag_):
        tag = Tag.objects.get(tag=tag_)
        return self.filter(tags__tag__in=[tag_]).distinct(), tag

    def get_one_question(self, question_id):
        question = self.get(id=question_id)
        answers = Answer.objects.filter(question=question_id).order_by('-id')
        return question, answers


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=1000)
    rating = models.IntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)
    answer_count = models.IntegerField(default=0)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    votes = GenericRelation('Like', related_query_name='question')

    objects = QuestionManager()

    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    vote = GenericRelation('Like', related_query_name='answer')

    def __str__(self):
        return str(self.question) + " - " + self.text[:10] + "..."


class TagManager(models.Manager):
    def get_best_tags(self, top_n=6):
        return self.annotate(questions_count=Count('question')).order_by('-questions_count')[:top_n]


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)

    objects = TagManager()

    def __str__(self):
        return self.tag


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class ProfileManager(models.Manager):
    def get_best_members(self, top_n=6):
        return self.annotate(answers_count=Count('answer')).order_by('-answers_count')[:top_n]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=16)
    avatar = models.FileField(upload_to=user_directory_path)

    objects = ProfileManager()

    def __str__(self):
        return self.nickname

    def get_avatar_url(self):
        return self.avatar.url


class LikeManager(models.Manager):
    use_for_related_fields = True

    def sum_rating(self):
        return self.get_queryset().aggregate(Sum('vote')).get('vote_sum') or 0


class Like(models.Model):
    votes = ((1, 'Like'), (-1, 'Dislike'))
    vote = models.IntegerField(choices=votes)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeManager()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id',)
