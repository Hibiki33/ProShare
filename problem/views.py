from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import *

import logging

# Create your views here.


def main_view(request):
    return render(request, 'problems.html')


def problem_lib_page(request):
    if request.method == 'GET':
        return render(request, 'problem_group_list.html')
    elif request.method == 'POST':
        pass


def problem_detail_page(request, id):
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
            "Submit": question.submission_number,
            "Passed": question.passed_number,
        }
        logging.debug('problem detail: ')
        logging.info(msg)

        return render(request, 'problem_detail.html', {'problem_info': msg})
    elif Problem.objects.filter(_id=id).exists:
        problem = Problem.objects.get(_id=id)
        # TODO
        raise NotImplementedError
    else:
        raise ModuleNotFoundError


def problem_create_page(request):
    if request.method == 'GET':
        return render(request, 'problem_create.html')
    elif request.method == 'POST':
        logging.debug('create problem request: ')
        logging.info(request.POST)

        # q = Question.objects.create(
        #     description=request.POST.get('description', ''),
        #     title=request.POST.get('question_title', ''),
        #     difficulty="middle",
        #     created_by=request.user,
        #     type=request.POST.get('type', 1),
        #     options=request.POST.get('choice', ''),
        #     answer=request.POST.get('question_answer', ''),
        # )

        # return HttpResponseRedirect('/problem/'+ str(q._id) + '/')
        return HttpResponse('Create Success!')


def problem_upload_page(request):
    if request.method == 'GET':
        return render(request, 'problem_upload.html')
    elif request.method == 'POST':
        file_name = request.POST.get('file', '')
        file = request.FILES.get('file', None)

        if not file:
            messages.error(request, 'No file uploaded!')
            return HttpResponseRedirect('/problem/problem_upload/')

        ProblemFile.objects.create(file_name=file_name,
                                   file=file)
        handle_uploaded_file(file)

        return HttpResponse('Upload Success!')


def handle_uploaded_file(f):
    # TODO: 这里文件打开方式是b 自己处理一下
    for line in f:
        print(line)
