from django.db.models import QuerySet
from ProShare.settings import MEDIA_ROOT
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
from .models import *
from .utils import list_msg, detail_msg
import os
import logging


# def main_view(request):
#     return render(request, 'problems.html')


def problem_main_page(request):
    if request.method == 'GET':
        return render(request, 'problem_list.html', {
            'problem_info_list': list_msg(request)})
    elif request.method == 'POST':
        is_op = request.POST.get('is_op', 'no')

        if is_op == 'yes':
            info = request.POST.get('search_info', '')

            order = request.POST.get('order', 'time')
            question_type = request.POST.get('question_type', 'all')
            question_diff = request.POST.get('question_diff', 'all')

            tag1 = request.POST.get('tag1', 'all')
            tag2 = request.POST.get('tag2', 'all')
            tag3 = request.POST.get('tag3', 'all')
            # _questions = Question.objects.all()
            # questions = []
            # for _q in _questions:
            #     if tag1 != 'all' and tag1 not in _q.tags.all():
            #         continue
            #     if tag2 != 'all' and tag2 not in _q.tags.all():
            #         continue
            #     if tag3 != 'all' and tag3 not in _q.tags.all():
            #         continue
            #     questions.append(_q)
            #
            # questions = QuerySet(questions)

            questions = Question.objects.all()
            if tag1 != 'all':
                questions = questions.filter(tags__name=tag1)
            if tag2 != 'all':
                questions = questions.filter(tags__name=tag2)
            if tag3 != 'all':
                questions = questions.filter(tags__name=tag3)

            if not info:
                return render(request, 'problem_list.html', {
                    'problem_info_list': list_msg(request,
                                                  questions=questions,
                                                  order=order,
                                                  difficulty=question_diff,
                                                  type=question_type)})

            return render(request, 'problem_list.html', {
                'problem_info_list': list_msg(request,
                                              questions=questions,
                                              order=order,
                                              difficulty=question_diff,
                                              type=question_type,
                                              search=info)})

        elif is_op == 'no':
            info = request.POST.get('search_info')

            if not info:
                return render(request, 'problem_list.html', {
                    'problem_info_list': list_msg(request)})
            return render(request, 'problem_list.html', {
                'problem_info_list': list_msg(request,
                                              search=info)})


def problem_detail_page(request, id):
    if request.method == 'GET':
        return render(request, 'problem_detail.html', {'problem_info': detail_msg(request, id)})
    elif request.method == 'POST':
        post: QueryDict = request.POST
        logging.debug('problem submit request: ')
        logging.info(post)
        if Question.objects.filter(_id=id).exists():
            verdict = 'System Error'
            question = Question.objects.get(_id=id)
            question.add_submission_number()
            msg = {}
            if question.type == 'single-choice' or question.type == 'multiple-choice':
                choice = post.getlist('choice')
                msg['Answer'] = ' '.join(choice)
                msg['Correct'] = ' '.join(question.correct_options)
                if set(choice) == set(question.correct_options):
                    # maintain question related user information
                    request.user.remove_wrong_question(question)
                    request.user.finish_questions_cnt += 1
                    request.user.save()

                    verdict = 'Accepted'
                    question.add_ac_number()
                else:
                    # maintain question related user information
                    request.user.add_wrong_question(question)
                    request.user.finish_questions_cnt += 1
                    request.user.wrong_questions_cnt += 1
                    request.user.save()

                    verdict = 'Wrong Answer'
            elif question.type == 'fill-blank':
                answer = post.get('answer')
                msg['Answer'] = answer
                msg['Correct'] = question.answer
                if answer == question.answer:
                    # maintain question related user information
                    request.user.remove_wrong_question(question)
                    request.user.finish_questions_cnt += 1
                    request.user.save()

                    verdict = 'Accepted'
                    question.add_ac_number()
                else:
                    # maintain question related user information
                    request.user.add_wrong_question(question)
                    request.user.finish_questions_cnt += 1
                    request.user.wrong_questions_cnt += 1
                    request.user.save()

                    verdict = 'Wrong Answer'
            else:
                verdict = 'System Error'
                return render(request, '404.html')
            msg['Verdict'] = verdict
            msg.update(detail_msg(request, id))
            return render(request, 'problem_result.html', {'problem_info': msg})
        elif Problem.objects.filter(_id=id).exists:
            problem = Problem.objects.get(_id=id)
            # TODO
            raise NotImplementedError
        else:
            raise FileNotFoundError


def problem_create_page(request):
    if request.method == 'GET':
        return render(request, 'problem_create.html')
    elif request.method == 'POST':
        post: QueryDict = request.POST
        logging.debug('create problem request: ')
        logging.info(post)
        q = Question.objects.create(
            description=post.get('question_description', 'NULL'),
            title=post.get('question_title', ''),
            difficulty=post.get('question_diff', 1),
            created_by=request.user,
            type=post.get('question_type', 1),
            options=list(filter(None, post.getlist('options', ['']))),
            answer=post.get('question_answer', ''),
        )
        q.set_correct_options(post.getlist('place', []))
        return HttpResponseRedirect('/problem/' + str(q._id) + '/')


def problem_upload_page(request):
    if request.method == 'GET':
        return render(request, 'problem_upload.html')
    elif request.method == 'POST':
        # file_name = request.POST.get('file', '')
        file = request.FILES.get('file', None)

        if not file:
            messages.error(request, 'No file uploaded!')
            return HttpResponseRedirect('/problem/problem_upload/')

        try:
            os.remove(MEDIA_ROOT / file.name)
        except FileNotFoundError:
            pass

        # file_name, file_extension = os.path.splitext(file.name)
        # file_path = MEDIA_ROOT / (file_name + '_' + timezone.now().strftime('%Y_%m_%d_%H_%M_%S') + file_extension)

        # with open(file_path, 'w+', encoding='utf-8') as f:
        #     f.write(file.read().decode('utf-8'))

        ProblemFile.objects.create(file_name=file.name,
                                   file=file)

        problems = []
        with open(MEDIA_ROOT / file.name, 'r+') as source:
            '''
            title: str
            description: str
            difficulty: 'Easy' | 'Middle' | 'Hard'
            type: 0 | 1 | 2
            { 
                options: [ str, str, str, str ],    type = 0, 1
            }
            answer: {
                        ABCD, type = 0, 1
                        str, type = 2
                    } 
            '''
            line = source.readline()
            line_cnt = 1
            status = 0
            problem = {}
            while line:
                if line.startswith('Title'):
                    if status != 0:
                        messages.error(
                            request, 'Error at %d: Unexpected Title' % line_cnt)
                        return HttpResponseRedirect('./')
                    _, title = line.split(':')
                    title = title.strip()
                    problem['title'] = title
                    status = 1

                elif line.startswith('Description'):
                    if status != 1:
                        messages.error(
                            request, 'Error at %d: Unexpected Description' % line_cnt)
                        return HttpResponseRedirect('./')
                    _, description = line.split(':')
                    description = description.strip()
                    problem['description'] = description
                    status = 2

                elif line.startswith('Difficulty'):
                    if status != 2:
                        messages.error(
                            request, 'Error at %d: Unexpected Difficulty' % line_cnt)
                        return HttpResponseRedirect('./')
                    _, difficulty = line.split(':')
                    difficulty = difficulty.strip()
                    if difficulty not in ['Easy', 'Middle', 'Hard']:
                        messages.error(
                            request, 'Error at %d: Invalid Difficulty' % line_cnt)
                        return HttpResponseRedirect('./')
                    problem['difficulty'] = difficulty
                    status = 3

                elif line.startswith('Type'):
                    if status != 3:
                        messages.error(
                            request, 'Error at %d: Unexpected Type' % line_cnt)
                        return HttpResponseRedirect('./')
                    _, _type = line.split(':')
                    _type = _type.strip()
                    if type not in ['0', '1', '2']:
                        messages.error(
                            request, 'Error at %d: Invalid Type' % line_cnt)
                        return HttpResponseRedirect('./')
                    problem['type'] = _type

                    if type == '0' or type == '1':
                        line = source.readline()
                        if not line.startswith('Options'):
                            messages.error(
                                request, 'Error at %d: Unexpected Options' % line_cnt)
                            return HttpResponseRedirect('./')
                        # TODO: 懒得处理 A. 这种了
                        options = list(line.split())
                        problem['options'] = options
                    status = 4

                elif line.startswith('Answer'):
                    if status != 4:
                        messages.error(
                            request, 'Error at %d: Unexpected Answer' % line_cnt)
                        return HttpResponseRedirect('./')
                    _, answer = line.split(':')
                    answer = answer.strip()
                    problem['answer'] = answer
                    problems.append(problem)
                    problem = {}
                    status = 0

                line = source.readline()
                line_cnt += 1

        # TODO: 把 problems 里的问题存到数据库里

        return HttpResponse('Upload Success!')


def problem_set_list_page(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
