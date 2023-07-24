from django.shortcuts import render

from .models import *

# Create your views here.

def main_view(request):
    return render(request, 'problems.html')

def problem_lib_page(request):
    if request.method == 'GET':
        return render(request, 'problem_group_list.html')
    elif request.method == 'POST':
        pass

def detail(request, id):
    if request.method == 'GET':
        return detail_view(request, id)
    elif request.method == 'POST':
        pass

def detail_view(request, id):
    if Question.objects.filter(_id=id).exists():
        question = Question.objects.get(_id=id)
        msg = {
            "ID": question._id,
            "Name": question.title,
            "Time": question.create_time,
            "Diff": question.difficulty,
            "Uploader": question.created_by,
            "Type": question.type,
            "Description": question.description,
            "Options": question.options,
            "Submit": 10, # TODO
            "Passed": 5, # TODO
        }
        return render(request, 'question.html', msg)
    elif Problem.objects.filter(_id=id).exists:
        problem = Problem.objects.get(_id=id)
        # TODO
        raise NotImplementedError
    else:
        raise ModuleNotFoundError