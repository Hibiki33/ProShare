import os

from django.db.models import QuerySet
from guardian.shortcuts import assign_perm
from ProShare.settings import MEDIA_ROOT
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render
from account.models import Punlum, PunlumNote
from .models import *
from .utils import list_msg, detail_msg, parse_file
import logging


# def main_view(request):
#     return render(request, 'problems.html')


def problem_main_page(request):
    if request.method == 'GET':
        return render(request, 'problem_list.html', {
            'problem_info_list': list_msg(request),
            'tag_list': [tag.name for tag in QuestionTag.objects.all()]
        })
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
        try:
            return render(request, 'problem_detail.html', {'problem_info': detail_msg(request, id)})
        except:
            return render(request, '404.html')
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

                    # maintain punlum
                    # PunlumNote.objects.create(question_id=question._id,
                    #                           punlum=Punlum.objects.get(user=request.user))
                    if not PunlumNote.objects.filter(question_id=question._id).exists():
                        PunlumNote.objects.create(question_id=question._id,
                                                  punlum=Punlum.objects.get(user=request.user))

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

                    if not PunlumNote.objects.filter(question_id=question._id).exists():
                        PunlumNote.objects.create(question_id=question._id,
                                                  punlum=Punlum.objects.get(user=request.user))

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


global upload_questions


def problem_create_page(request):
    if request.method == 'GET':
        return render(request, 'problem_create.html', {'tag_list': [tag.name for tag in QuestionTag.objects.all()]})
    elif request.method == 'POST':
        post: QueryDict = request.POST
        logging.debug('create problem request: ')
        logging.info(post)
        post_type = post.get('create_type')
        if post_type == 'edit-online':
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
            for i in range(1, 4):
                if not post.get(f'tag{i}') == 'none':
                    q.add_tag(post.get(f'tag{i}', ''))
            return HttpResponseRedirect('/problem/' + str(q._id) + '/')
        elif post_type == 'upload-file':
            global upload_questions
            file = request.FILES.get('files')

            try:
                os.remove(MEDIA_ROOT / file.name)
            except FileNotFoundError:
                pass

            ProblemFile.objects.create(
                file=file,
                file_name=file.name,
            )

            try:
                upload_questions = parse_file(file)
            except Exception as e:
                messages.warning(request, e)
                logging.info(e)
                return render(request, 'problem_create.html')

            msg = []
            for question in upload_questions:
                msg.append({
                    "ID": -1,
                    "Name": question['title'],
                    "Diff": question['difficulty'],
                    "Type": question['type'],
                    "Description": question['description'],
                    "Answer": question['answer'],
                })
                if 'options' in question.keys():
                    msg[-1]['Options'] = question['options']
                tags = question['tags']
                for i in range(3):
                    msg[-1][f'Tag{i + 1}'] = tags[i] if len(tags) > i else ''
            logging.debug('problem_info_list: ')
            logging.info(msg)
            return render(request, 'problem_file_preview.html', {'problem_info_list': msg})
        elif post_type == 'confirm':
            diff_table = {
                '0': 'Easy',
                '1': 'Medium',
                '2': 'Hard',
                '3': 'Expert',
                '4': 'Master',
                '5': 'Re-Master',
            }
            type_table = {
                '0': 'single-choice',
                '1': 'multiple-choice',
                '2': 'fill-blank',
            }
            for question in upload_questions:
                if 'options' in question.keys():
                    q = Question.objects.create(
                        description=question['description'],
                        title=question['title'],
                        difficulty=diff_table[question['difficulty']],
                        created_by=request.user,
                        type=type_table[question['type']],
                        options=question['options'],
                        answer=question['answer'],
                        correct_options=question['answer'].split(),
                    )
                else:
                    q = Question.objects.create(
                        description=question['description'],
                        title=question['title'],
                        difficulty=diff_table[question['difficulty']],
                        created_by=request.user,
                        type=type_table[question['type']],
                        options="",
                        answer=question['answer'],
                        correct_options=[],
                    )
                for tag in question['tags']:
                    if QuestionTag.objects.filter(name=tag).exists():
                        q.add_tag(tag)
                    # q.add_tag(tag)
            return HttpResponseRedirect('/problem/')


def problem_set_list_page(request):
    if request.method == 'GET':
        user = request.user
        groups = user.groups.all()

        # check the user's perm to view
        # instead of check the attribute of 'belongs_to'
        problem_set_list = []
        # for group in groups:
        #     problem_set_list.extend(group.question_sets.all())
        #
        # for question_set in QuestionSet.objects.all():
        #     if question_set.belongs_to is None:
        #         problem_set_list.append(question_set)
        for question_set in QuestionSet.objects.all():
            if user.has_perm('problem.view_question_set', question_set):
                problem_set_list.append(question_set)

        problem_set_list = list(set(problem_set_list))

        return render(request, 'problem_set_list.html', locals())

    elif request.method == 'POST':
        # print(request.POST)
        # request.method = 'GET'
        # return problem_set_list_page(request)
        # <QueryDict: {'search_info': ['wfy'], 'search': [''], 'filter': ['name']}>
        search_info = request.POST.get('search_info')
        name_filter = 'name' in request.POST.get('filter')
        creator_filter = 'creator' in request.POST.get('filter')
        owner_filter = 'owner' in request.POST.get('filter')

        user = request.user
        problem_set_list = []

        if search_info:
            for question_set in QuestionSet.objects.all():
                if not user.has_perm('problem.view_question_set', question_set):
                    continue
                if (name_filter and search_info in question_set.name) or \
                        (creator_filter and search_info in question_set.created_by.username) or \
                        (owner_filter and search_info in question_set.belongs_to.name):
                    problem_set_list.append(question_set)
        else:
            for question_set in QuestionSet.objects.all():
                if user.has_perm('problem.view_question_set', question_set):
                    problem_set_list.append(question_set)

        problem_set_list = list(set(problem_set_list))

        return render(request, 'problem_set_list.html', locals())


def problem_set_detail_page(request, set_id):
    set_id = int(set_id)

    if request.method == 'GET':
        if QuestionSet.objects.filter(id=set_id).exists():
            question_set = QuestionSet.objects.get(id=set_id)
            questions = question_set.get_questions()
            problem_info_list = []
            for question in questions:
                problem_info_list.append(detail_msg(request, question._id))
            return render(request, 'problem_set_detail.html', {
                'name': question_set.name,
                'problem_info_list': problem_info_list,
                'modify': request.user.has_perm('problem.edit_question_set', question_set),
            })
        else:
            return render(request, '404.html')

    elif request.method == 'POST':
        if 'modify' in request.POST.keys():
            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/modify/')
        elif 'submit' in request.POST.keys():
            if QuestionSet.objects.filter(id=set_id).exists():
                question_set = QuestionSet.objects.get(id=set_id)
                questions = question_set.get_questions()
                cur_finished_cnt = 0
                cur_correct_cnt = 0
                msgs = []
                for question in questions:
                    verdict = 'System Error'
                    question.add_submission_number()
                    msg = {}
                    if question.type == 'single-choice' or question.type == 'multiple-choice':
                        choice = request.POST.getlist(
                            'choice' + str(question._id))
                        msg['Answer'] = ' '.join(choice)
                        msg['Correct'] = ' '.join(question.correct_options)
                        if set(choice) == set(question.correct_options):
                            # maintain question related user information
                            request.user.remove_wrong_question(question)
                            request.user.finish_questions_cnt += 1
                            request.user.save()
                            cur_finished_cnt += 1
                            cur_correct_cnt += 1

                            verdict = 'Accepted'
                            question.add_ac_number()

                        else:
                            # maintain question related user information
                            request.user.add_wrong_question(question)
                            request.user.finish_questions_cnt += 1
                            request.user.wrong_questions_cnt += 1
                            request.user.save()
                            cur_finished_cnt += 1

                            verdict = 'Wrong Answer'

                    elif question.type == 'fill-blank':
                        answer = request.POST.get('answer' + str(question._id))
                        msg['Answer'] = answer
                        msg['Correct'] = question.answer
                        if answer == question.answer:
                            # maintain question related user information
                            request.user.remove_wrong_question(question)
                            request.user.finish_questions_cnt += 1
                            request.user.save()
                            cur_finished_cnt += 1
                            cur_correct_cnt += 1

                            verdict = 'Accepted'
                            question.add_ac_number()

                        else:
                            # maintain question related user information
                            request.user.add_wrong_question(question)
                            request.user.finish_questions_cnt += 1
                            request.user.wrong_questions_cnt += 1
                            request.user.save()
                            cur_finished_cnt += 1

                            verdict = 'Wrong Answer'

                    else:
                        verdict = 'System Error'
                        return render(request, '404.html')

                    msg['Verdict'] = verdict
                    msg.update(detail_msg(request, question._id))

                    msgs.append(msg)

                return render(request, 'problem_set_result.html', {
                    'problem_info_list': msgs,
                    'ResultStr': f"{cur_correct_cnt}/{cur_finished_cnt}"
                })

            else:
                return render(request, '404.html')


def problem_set_create_page(request):
    if request.method == 'GET':
        # if temp_set_id is None:
        #     temp_question_set = TempQuestionSet.objects.create(
        #         name=None,
        #         group_name='public', )
        # else:
        #     temp_question_set = QuestionSet.objects.get(id=temp_set_id)
        #
        # questions = temp_question_set.get_questions()
        #
        # return render(request, 'problem_set_create.html', {
        #     'id': temp_question_set.id,
        #     'name': temp_question_set.name,
        #     'groups': request.user.groups.all(),
        #     'problem_info_list': list_msg(request, questions=questions),
        # })

        return render(request, 'problem_set_create.html', {'groups': request.user.groups.all()})

    elif request.method == 'POST':
        question_set_name = request.POST.get('name')
        group_name = request.POST.get('set_type', 'public')
        # print("\n\n\n\n\nGROUP_NAME:", group_name)

        if not question_set_name:
            messages.error(request, 'Question Set\'s name cannot be empty!')
            return HttpResponseRedirect('/problem/set/create/')

        question_set = QuestionSet.objects.create(
            name=question_set_name,
            belongs_to=Group.objects.get(
                name=group_name) if group_name != 'public' else None,
            created_by=request.user
        )

        # assign the perm to user and group
        # the creator should have the perm to edit
        assign_perm('problem.edit_question_set', request.user, question_set)
        # the certain group should have the perm to view (or public)
        if group_name == 'public':
            for group in Group.objects.all():
                assign_perm('problem.view_question_set', group, question_set)
        else:
            assign_perm('problem.view_question_set',
                        Group.objects.get(name=group_name), question_set)

        return HttpResponseRedirect('/problem/set/' + str(question_set.id) + '/' + 'modify/add')

        # temp_id = request.POST.get('id')
        # temp_question_set = TempQuestionSet.objects.get(id=temp_id)
        #
        # if group_name != 'public':
        #     temp_question_set.group_name = group_name
        #     temp_question_set.save()
        #
        # if 'add' in request.POST.keys():
        #     if question_set_name:
        #         temp_question_set.name = question_set_name
        #         temp_question_set.save()
        #
        #     return HttpResponseRedirect('/problem/set/create/add', {
        #         'id': temp_id,
        #         'mode': 'create',
        #     })
        # elif 'confirm' in request.POST.keys():
        #     if question_set_name:
        #         temp_question_set.name = question_set_name
        #         temp_question_set.save()
        #     else:
        #         messages.error(request, 'Question Set\'s name cannot be empty!')
        #         request.method = 'GET'
        #         return problem_set_create_page(request, temp_id)
        #
        #     return HttpResponseRedirect('/problem/set/')


def problem_set_modify_page(request, set_id):
    set_id = int(set_id)

    if request.method == 'GET':
        question_set = QuestionSet.objects.get(id=set_id)
        questions = question_set.get_questions()
        return render(request, 'problem_set_modify.html', {
            'name': question_set.name,
            'belongs_to': question_set.belongs_to.name if question_set.belongs_to else 'public',
            'groups': request.user.groups.all(),
            'problem_info_list': list_msg(request, questions=questions),
        })

    elif request.method == 'POST':
        if 'remove' in request.POST.keys():
            question_id = request.POST.get('remove')
            question_set = QuestionSet.objects.get(id=set_id)
            question_set.remove_question(Question.objects.get(_id=question_id))
            question_set.save()
            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/modify/')

        elif 'confirm' in request.POST.keys():
            question_set = QuestionSet.objects.get(id=set_id)
            question_set_name = request.POST.get('name')
            group_name = request.POST.get('set_type', 'public')

            question_set.name = question_set_name
            question_set.belongs_to = Group.objects.get(
                name=group_name) if group_name != 'public' else None
            question_set.save()

            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/')

        elif 'add' in request.POST.keys():
            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/modify/add/')


def problem_set_modify_add_page(request, set_id):
    set_id = int(set_id)
    question_set = QuestionSet.objects.get(id=set_id)

    if request.method == 'GET':
        return render(request, 'problem_set_findadd.html', {
            'problem_info_list': list_msg(request)
        })

    elif request.method == 'POST':
        if 'add' in request.POST.keys():
            choices = request.POST.getlist('choice')
            for choice in choices:
                question_set.add_question(Question.objects.get(_id=choice))

            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/modify/add/')

        elif 'search' in request.POST.keys():
            is_op = request.POST.get('is_op', 'no')

            if is_op == 'yes':
                info = request.POST.get('search_info', '')

                order = request.POST.get('order', 'time')
                question_type = request.POST.get('question_type', 'all')
                question_diff = request.POST.get('question_diff', 'all')

                tag1 = request.POST.get('tag1', 'all')
                tag2 = request.POST.get('tag2', 'all')
                tag3 = request.POST.get('tag3', 'all')

                questions = Question.objects.all()
                if tag1 != 'all':
                    questions = questions.filter(tags__name=tag1)
                if tag2 != 'all':
                    questions = questions.filter(tags__name=tag2)
                if tag3 != 'all':
                    questions = questions.filter(tags__name=tag3)

                if not info:
                    return render(request, 'problem_set_findadd.html', {
                        'problem_info_list': list_msg(request,
                                                      questions=questions,
                                                      order=order,
                                                      difficulty=question_diff,
                                                      type=question_type)})

                return render(request, 'problem_set_findadd.html', {
                    'problem_info_list': list_msg(request,
                                                  questions=questions,
                                                  order=order,
                                                  difficulty=question_diff,
                                                  type=question_type,
                                                  search=info)})

            elif is_op == 'no':
                info = request.POST.get('search_info')

                if not info:
                    return render(request, 'problem_set_findadd.html', {
                        'problem_info_list': list_msg(request)})
                return render(request, 'problem_set_findadd.html', {
                    'problem_info_list': list_msg(request,
                                                  search=info)})
        elif 'confirm' in request.POST.keys():
            return HttpResponseRedirect('/problem/set/' + str(set_id) + '/modify/')
