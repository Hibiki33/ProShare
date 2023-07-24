from django.db import models


class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    content = models.TextField()

    # the following is used to confirm whether there is a standard answer
    std_ans = models.BooleanField(default=False)
    answer = models.TextField(blank=True)

    # the following indicates the create and update time
    # in case of using `.objects.filter().update()` method,
    #   update time won't change automatically,
    #   thus we need to use `auto_now` to update the update time.
    # if we use `.save()` method,
    #   update time will change automatically,
    #   but I don't know if `save()` will create a new question or not.
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    author = models.ForeignKey('account.User', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.question_id) + ' ' + self.title
