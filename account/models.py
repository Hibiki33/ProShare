from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

from utils.models import RichTextField


# class UserInfo(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     user_name = models.CharField(max_length=20)
#     user_password = models.CharField(max_length=20)
#     user_mail = models.CharField(max_length=20)
#     user_phone = models.CharField(max_length=20)
#
#     user_quote = models.CharField(max_length=128)


class UserManager(BaseUserManager):
    def _create_user(self, username, password, email, **extra_fields):
        if not username:
            raise ValueError('Username must be set!')
        if not password:
            raise ValueError('Password must be set!')
        if not email:
            raise ValueError('Email must be set!')

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, **extra_fields):
        extra_fields['is_superuser'] = False
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields['is_superuser'] = True
        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    phone = RichTextField(max_length=11, null=True, blank=True)
    quote = models.TextField(max_length=128, null=True, blank=True)

    wrong_problems = models.ManyToManyField("problem.Problem", blank=True)
    wrong_questions = models.ManyToManyField("problem.Question", blank=True)

    finish_questions_cnt = models.IntegerField(default=0)
    wrong_questions_cnt = models.IntegerField(default=0)

    def set_quote(self, quote):
        self.quote = quote
        self.save()

    def set_phone(self, phone):
        self.phone = phone
        self.save()

    def get_quote(self):
        return self.quote

    def get_phone(self):
        return self.phone

    def add_wrong_question(self, question):
        self.wrong_questions.add(question)
        self.save()

    def add_wrong_problem(self, problem):
        self.wrong_problems.add(problem)
        self.save()

    def remove_wrong_question(self, question):
        if self.is_wrong_question(question):
            self.wrong_questions.remove(question)
            self.save()

    def remove_wrong_problem(self, problem):
        if self.is_wrong_problem(problem):
            self.wrong_problems.remove(problem)
            self.save()

    def get_wrong_questions(self):
        return self.wrong_questions.all()

    def get_wrong_problems(self):
        return self.wrong_problems.all()

    def is_wrong_question(self, question):
        return question in self.wrong_questions.all()

    def is_wrong_problem(self, problem):
        return problem in self.wrong_problems.all()

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class Punlum(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class PunlumNote(models.Model):
    question_id = models.IntegerField()
    question_note = models.TextField(max_length=1024, null=True, blank=True)

    punlum = models.ForeignKey(Punlum, on_delete=models.CASCADE, related_name="notes")
