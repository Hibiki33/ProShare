from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


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
    phone = models.CharField(max_length=11, null=True, blank=True)
    quote = models.TextField(max_length=128, null=True, blank=True)

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

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

