from django import forms
from django.contrib.auth.models import User

from app.models import Profile, Question, Answer, Like, ContentType, F


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if username.strip() == '':
            raise forms.ValidationError('Empty username', code='empty_username_error')
        elif len(username) < 5:
            raise forms.ValidationError('Short username', code='short_username_error')
        elif ' ' in username:
            raise forms.ValidationError('Space in username', code='space_in_username_error')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if password.strip() == '':
            raise forms.ValidationError('Empty password', code='empty_password_error')
        elif len(password) < 5:
            raise forms.ValidationError('Short password', code='short_password_error')
        elif ' ' in password:
            raise forms.ValidationError('Space in password', code='space_in_password_error')
        return password


class SignUpForm(forms.Form):
    username = forms.CharField()
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    # avatar

    def clean_username(self):
        username = self.cleaned_data['username']
        if username.strip() == '':
            raise forms.ValidationError('Empty username', code='empty_username_error')
        elif len(username) < 5:
            raise forms.ValidationError('Short username', code='short_username_error')
        elif ' ' in username:
            raise forms.ValidationError('Space in username', code='space_in_username_error')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email.strip() == '':
            raise forms.ValidationError('Empty email', code='empty_email_error')
        elif ' ' in email:
            raise forms.ValidationError('Space in email', code='space_in_email_error')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        if password.strip() == '':
            raise forms.ValidationError('Empty password', code='empty_password_error')
        elif len(password) < 5:
            raise forms.ValidationError('Short password', code='short_password_error')
        elif ' ' in password:
            raise forms.ValidationError('Space in password', code='space_in_password_error')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')
        if password != repeat_password:
            raise forms.ValidationError("Passwords don't match")

    def save(self, commit=True):
        user = User.objects.create_user(username=self.cleaned_data.get('username'),
                                        email=self.cleaned_data.get('email'),
                                        password=self.cleaned_data.get('password'))
        profile = Profile(user=user)

        if commit:
            user.save()
            profile.save()

        return user, profile


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = Question(title=self.cleaned_data.get('title'),
                            text=self.cleaned_data.get('text'))
        question.profile = Profile.objects.get(user=self.user)
        if commit:
            question.save()

        question.tags.set(self.cleaned_data.get('tags'))
        if commit:
            question.save()

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

    def __init__(self, user, question, *args, **kwargs):
        self.user = user
        self.question = question
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = Answer(text=self.cleaned_data.get('text'))
        answer.profile = Profile.objects.get(user=self.user)
        question = self.question
        question.answer_count += 1
        question.save()
        answer.question = question
        answer.is_correct = False
        if commit:
            answer.save()
        return answer


class SettingsForm(forms.ModelForm):
    nickname = forms.CharField()
    avatar = forms.ImageField()

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if nickname.strip() == '':
            raise forms.ValidationError('Nickname is empty', code='validation_error')
        return nickname

    class Meta:
        model = User
        fields = ['nickname', 'email', 'avatar']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.user.profile.nickname = self.cleaned_data.get('nickname')
        self.user.profile.avatar = self.cleaned_data.get('avatar')
        if commit:
            self.user.profile.save()
        return self.user


class LikeForm(forms.Form):
    pk = forms.IntegerField()
    action = forms.CharField()
    content = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        pk = int(self.cleaned_data.get('pk', -1))
        action = self.cleaned_data.get('action', '')
        if pk == -1 or action == '':
            return 0
        inc = Like.objects.get_increment(action)

        content = self.cleaned_data.get('content')
        if content == 'question':
            q = Question.objects.get(pk=pk)
            try:
                q_set = Question.objects.filter(id=pk)
                q_type = ContentType.objects.get_for_model(Question)
                obj = Like.objects.get(content_type__pk=q_type.id, object_id__in=q_set, user=self.user)
                inc = 0 if inc == obj.vote else 2 if obj.vote == -1 else -2
                obj.vote = Like.objects.get_increment(action)
                if commit:
                    obj.save()
            except:
                like = Like(content_object=q, vote=inc, user=self.user)
                like.save()

            q.rating = F('rating') + inc
            if commit:
                q.save()
            return Question.objects.get(pk=pk).rating

        elif content == 'answer':
            a = Answer.objects.get(pk=pk)
            try:
                a_set = Answer.objects.filter(id=pk)
                a_type = ContentType.objects.get_for_model(Answer)
                obj = Like.objects.get(content_type__pk=a_type.id, object_id__in=a_set, user=self.user)
                inc = 0 if inc == obj.vote else 2 if obj.vote == -1 else -2
                obj.vote = Like.objects.get_increment(action)
                if commit:
                    obj.save()
            except:
                like = Like(content_object=a, vote=inc, user=self.user)
                if commit:
                    like.save()

            a.rating = F('rating') + inc
            a.save()
            return Answer.objects.get(pk=pk).rating


class CorrectForm(forms.Form):
    pk = forms.IntegerField()
    is_correct = forms.BooleanField(required=False)

    def save(self, commit=True):
        answer = Answer.objects.get(pk=self.cleaned_data['pk'])
        answer.is_correct = self.cleaned_data['is_correct']
        if commit:
            answer.save()
        return answer
