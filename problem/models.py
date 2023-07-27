from django.db import models
from utils.models import RichTextField, JSONField
from account.models import User


class Question(models.Model):
    # display ID
    _id = models.AutoField(primary_key=True)
    title = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    difficulty = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.TextField()
    description = RichTextField()
    options = JSONField()
    answer = models.TextField()

    submission_number = models.BigIntegerField(default=0)
    passed_number = models.BigIntegerField(default=0)

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.passed_number = models.F("passed_number") + 1
        self.save(update_fields=["passed_number"])

    # class Meta:
    #     db_table = "question"
    #     ordering = ("create_time",)
    

class Problem(models.Model):
    # display ID
    _id = models.TextField()
    # # for contest problem
    # is_public = models.BooleanField(default=False)
    # title = models.TextField()
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.TextField()
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(null=True)
    languages = JSONField()
    template = JSONField()
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # special judge related
    spj = models.BooleanField(default=False)
    spj_language = models.TextField(null=True)
    spj_code = models.TextField(null=True)
    spj_version = models.TextField(null=True)
    spj_compile_ok = models.BooleanField(default=False)
    rule_type = models.TextField()
    visible = models.BooleanField(default=True)
    difficulty = models.TextField()
    # tags = models.ManyToManyField(ProblemTag) TODO
    source = models.TextField(null=True)
    # for OI mode
    total_score = models.IntegerField(default=0)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)
    share_submission = models.BooleanField(default=False)

    # class Meta:
    #     db_table = "problem"
    #     ordering = ("create_time",)

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save(update_fields=["accepted_number"])


class ProblemFile(models.Model):
    file_name = models.CharField(max_length=128)
    file = models.FileField()
