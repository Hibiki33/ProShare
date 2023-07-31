from django.contrib.auth.models import Group
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
    correct_options = JSONField(default=list)
    answer = models.TextField()

    submission_number = models.BigIntegerField(default=0)
    passed_number = models.BigIntegerField(default=0)

    tags = models.ManyToManyField("QuestionTag")

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.passed_number = models.F("passed_number") + 1
        self.save(update_fields=["passed_number"])

    def set_correct_options(self, place):
        self.correct_options = [self.options[ord(i) - ord('A')] for i in place]
        self.save()

    def add_tag(self, tagname):
        tag = QuestionTag.objects.get(name=tagname)
        self.tags.add(tag)
        tag.add_question(self)

    def has_tag(self, tagname):
        try:
            tag = QuestionTag.objects.get(name=tagname)
        except QuestionTag.DoesNotExist:
            return False
        return tag in self.tags.all()

    # class Meta:
    #     db_table = "question"
    #     ordering = ("create_time",)
    class Meta:
        default_permissions = ()
        permissions = (
            ("view_question", "Can view question"),
            ("edit_question", "Can edit question"),
        )


class QuestionSet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_sets')
    # belongs_to = None indicated public?
    # above
    belongs_to = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name='question_sets')
    questions = models.ManyToManyField(Question)

    def add_question(self, question):
        self.questions.add(question)
        self.save()

    def add_questions(self, questions):
        for question in questions:
            self.add_question(question)
        self.save()

    def remove_question(self, question):
        self.questions.remove(question)
        self.save()

    def remove_questions(self, questions):
        for question in questions:
            self.remove_question(question)
        self.save()

    def get_questions(self):
        return self.questions.all()

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_question_set", "Can view question_set"),
            ("edit_question_set", "Can edit question_set"),
        )


# class TempQuestionSet(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=128, null=True)
#
#     group_name = models.CharField(max_length=128, null=True)
#     questions = models.ManyToManyField(Question)
#
#     def add_question(self, question):
#         self.questions.add(question)
#         self.save()
#
#     def add_questions(self, questions):
#         for question in questions:
#             self.add_question(question)
#         self.save()
#
#     def remove_question(self, question):
#         self.questions.remove(question)
#         self.save()
#
#     def remove_questions(self, questions):
#         for question in questions:
#             self.remove_question(question)
#         self.save()
#
#     def get_questions(self):
#         return self.questions.all()
#
#     class Meta:
#         default_permissions = ()
#         permissions = (
#             ("view_question_set", "Can view question_set"),
#             ("edit_question_set", "Can edit question_set"),
#         )


class QuestionTag(models.Model):
    name = models.CharField(max_length=128, primary_key=True)
    questions = models.ManyToManyField(Question, blank=True)

    def add_question(self, question):
        self.questions.add(question)
        self.save()

    # for tranfer of student's ability
    # chosen in 0, 1, 2, 3, 4, 5, set by admin
    # basic knowledge, logical thinking, problem skills, detailed analysis, summarization, comprehensive ability
    ability = models.IntegerField(default=0)

    # class Meta:
    #     db_table = "question_tag"
    

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

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_question", "Can view question"),
            ("edit_question", "Can edit question"),
        )


class ProblemSet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    problems = models.ManyToManyField(Problem)

    def add_problem(self, problem):
        self.problems.add(problem)
        self.save()

    def add_problems(self, problems):
        for problem in problems:
            self.add_problem(problem)
        self.save()

    def remove_problem(self, problem):
        self.problems.remove(problem)
        self.save()

    def remove_problems(self, problems):
        for problem in problems:
            self.remove_problem(problem)
        self.save()

    def get_problems(self):
        return self.problems.all()


class ProblemFile(models.Model):
    file_name = models.CharField(max_length=128)
    file = models.FileField()
