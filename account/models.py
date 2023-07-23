from django.db import models


class UserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=20)
    user_password = models.CharField(max_length=20)
    user_mail = models.CharField(max_length=20)
    user_phone = models.CharField(max_length=20)

    user_quote = models.CharField(max_length=128)
