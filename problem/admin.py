from django.contrib import admin
from .models import ProblemFile, Problem, Question, QuestionTag

admin.site.site_header = 'Problem Admin'
admin.site.register(ProblemFile)
admin.site.register(Problem)
admin.site.register(Question)
admin.site.register(QuestionTag)
