from math import log2

from django.contrib.auth.models import Group
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model

from .utils import gen_ability_map
from problem.models import Question, QuestionSet
from .models import Punlum, PunlumNote
import uuid
import logging
from problem.utils import list_msg

User = get_user_model()


def get_uuid(length=8):
    return str(uuid.uuid4()).replace('-', '')[:length]


# def login_view(request):
#     return render(request, 'login.html')


def login_page(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        # login_name = request.POST.get('username', '')
        # login_password = request.POST.get('password', '')
        # print(login_name, login_password)

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            # return render(request, 'abort_login.html', {'message': 'user_name or password is empty!'})
            messages.error(request, 'Username or Password is empty!')
            return HttpResponseRedirect('/account/login/')

        # success: return a user object
        # false: return None
        user = authenticate(request, username=username, password=password)

        # if User.objects.filter(user_name=login_name, user_password=login_password).count() != 0:
        #     return redirect('../../')
        # else:
        #     # return render(request, 'abort_login.html', {'message': 'user_name or password is wrong!'})
        #     messages.error(request, 'user_name or password is wrong!')
        #     return HttpResponseRedirect('/account/login/')

        if user:
            login(request, user)
            request.session['username'] = username
            request.session.set_expiry(0)
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Username or Password is wrong!')
            return HttpResponseRedirect('/account/login/')

    return render(request, '404.html')


# def register_view(request):
#     return render(request, 'register.html')


def register_page(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        email = request.POST.get('email', '')

        if password != confirm_password:
            # return render(request, 'abort_register.html', {'message': 'password and confirm_password is not same!'})
            messages.error(
                request, 'password and confirm_password is not same!')
            return HttpResponseRedirect('/account/register/')

        if not username or not password or not email:
            # return render(request, 'abort_register.html', {'message': 'name and password is necessary!'})
            messages.error(request, 'name, password and email is necessary!')
            return HttpResponseRedirect('/account/register/')

        # if User.objects.filter(user_name=user_name).count() != 0:
        #     # return render(request, 'abort_register.html', {'message': 'user_name is already exist!'})
        #     messages.error(request, 'user_name is already exist!')
        #     return HttpResponseRedirect('/account/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'username already exists!')
            return HttpResponseRedirect('/account/register/')

        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email,
                                        quote='',
                                        phone='', )

        Punlum.objects.create(user=user)

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            request.session['username'] = username
            request.session.set_expiry(0)
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Username or Password is wrong!')
            return HttpResponseRedirect('/account/login/')

        return HttpResponseRedirect('/account/')

    return render(request, '404.html')


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


# def change_password_view(request):
#     return render(request, 'change_password.html')


def change_password_page(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'change_password.html')
        else:
            return HttpResponseRedirect('/account/login/')
    elif request.method == 'POST':
        old_password = request.POST.get('prev_password', '')
        new_password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not old_password or not new_password or not confirm_password:
            messages.error(request, 'not finished!')
            return HttpResponseRedirect('/account/change_password/')

        if new_password != confirm_password:
            messages.error(
                request, 'new_password and confirm_password is not same!')
            return HttpResponseRedirect('/account/change_password/')

        user = authenticate(
            request, username=request.user.username, password=old_password)

        if user:
            user.set_password(new_password)
            user.save()
            return HttpResponseRedirect('/account/login/')
        else:
            messages.error(request, 'previous password is wrong!')
            return HttpResponseRedirect('/account/change_password/')


def edit_view(request):
    return render(request, 'home_edit.html')


def edit_page(request):
    post: dict = request.POST
    logging.debug('create problem request: ')
    logging.info(post)
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'home_edit.html')
        else:
            return HttpResponseRedirect('/account/login/')
    elif request.method == 'POST':
        if request.user.is_authenticated:
            quote = request.POST.get('quote', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')

            request.user.set_quote(quote)
            request.user.email = email
            request.user.set_phone(phone)
            request.user.save()
            return HttpResponseRedirect('/account/')
        else:
            return HttpResponseRedirect('/account/login/')


# def home_view(request):
#     return render(request, 'home.html')


def home_page(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/account/login/')


    total_answered = request.user.finish_questions_cnt
    total_wrong = request.user.wrong_questions_cnt

    user_ability = gen_ability_map(request.user, lack=True)
    for i in range(6):
        user_ability[i] = 0.2 if user_ability[i] < 0.2 else user_ability[i]
        user_ability[i] = {'val': user_ability[i]}

    average_ability = [0, 0, 0, 0, 0, 0]
    for user in User.objects.all():
        ability = gen_ability_map(user, lack=True)
        for i in range(6):
            average_ability[i] += ability[i]
    average_ability = [i / len(User.objects.all()) for i in average_ability]
    for i in range(6):
        average_ability[i] = 0.2 if average_ability[i] < 0.2 else average_ability[i]
        average_ability[i] = {'val': average_ability[i]}
    from problem.models import QuestionTag
    msg = {
        'username': request.user.username,
        'email': request.user.email,
        'phone': request.user.phone,
        'quote': request.user.quote,
        'groups': request.user.groups.all(),
        'total_answered': total_answered,
        'wrong_rate': format((total_answered - total_wrong) / total_answered * 100, '.2f')
        if total_answered != 0 else 0,
        'user_ability': user_ability,
        'average_ability': average_ability,
        'tag_list': [tag.name for tag in QuestionTag.objects.all()],
    }
    if request.method == 'GET':
        # test if wrong questions can be got
        # for q in request.user.wrong_questions.all():
        #     print(q.title)
        # for q in request.user.get_wrong_questions():
        #     print(q.title)
        total_answered = request.user.finish_questions_cnt
        total_wrong = request.user.wrong_questions_cnt

        user_ability = gen_ability_map(request.user, lack=True)
        for i in range(6):
            user_ability[i] = 0.2 if user_ability[i] < 0.2 else user_ability[i]
            user_ability[i] = {'val': user_ability[i]}

        average_ability = [0, 0, 0, 0, 0, 0]
        for user in User.objects.all():
            ability = gen_ability_map(user, lack=True)
            for i in range(6):
                average_ability[i] += ability[i]
        average_ability = [i / len(User.objects.all())
                            for i in average_ability]
        for i in range(6):
            average_ability[i] = 0.2 if average_ability[i] < 0.2 else average_ability[i]
            average_ability[i] = {'val': average_ability[i]}
        return render(request, 'home.html', msg)
    elif request.method == 'POST':
        if 'logout' in request.POST.keys():
            group_name = request.POST.get('exit')
            group = Group.objects.get(name=group_name)
            group.user_set.remove(request.user)
            return HttpResponseRedirect('/account/')
        elif 'generate' in request.POST.keys():
            number = request.POST.get('question_num', '10')
            tag_name = request.POST.get('tag')
            problem_info_list = list_msg(request, questions=request.user.get_recommended_questions(
                num=int(number),
                selected_tag=tag_name,
                cal_weight=lambda x: x * 2
            ))
            msg['problem_info_list'] = problem_info_list
            msg['selected_tag'] = tag_name
            return render(request, 'home.html', msg)
        elif 'exit' in request.POST.keys():
            group_name = request.POST.get('exit')
            group = Group.objects.get(name=group_name)
            group.user_set.remove(request.user)
            return HttpResponseRedirect('/account/')

        else:
            return HttpResponseRedirect('/account/')


def group_detail_page(request, group_name):
    if request.method == 'GET':
        if request.user.is_authenticated:
            group_question_sets = []
            group = Group.objects.get(name=group_name)
            for question_set in group.question_sets.all():
                group_question_sets.append(question_set)
            for question_set in QuestionSet.objects.all():
                if question_set.belongs_to is None:
                    group_question_sets.append(question_set)
            group_question_set = list(set(group_question_sets))
            return render(request, 'group_detail.html', {
                'group_name': group.name,
                'group_question_sets': group_question_set,
            })
        else:
            return HttpResponseRedirect('/account/login/')
    elif request.method == 'POST':
        pass


def group_search_page(request):
    if request.method == 'GET':
        search_info = request.GET.get('search_info')

        if not search_info:
            return render(request, 'group_search.html', locals())

        _search_result = Group.objects.filter(name__contains=search_info)

        search_result = []
        for i in _search_result:
            item = {'name': i.name,
                    'not_in_group': request.user.groups.filter(name=i.name).count() == 0}

            search_result.append(item)

        return render(request, 'group_search.html', locals())

    elif request.method == 'POST':
        selected_group_name = request.POST.get('selected_group')

        selected_group = Group.objects.get(name=selected_group_name)

        selected_group.user_set.add(request.user)

        request.method = 'GET'
        return group_search_page(request)


def punlum_page(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            punlum = request.user.punlum
            punlum_notes = punlum.notes.all()
            punlum_items = []
            for note in punlum_notes:
                try:
                    question = Question.objects.get(_id=note.question_id)
                except Question.DoesNotExist:
                    continue
                # print(question.title, question.difficulty)
                punlum_items.append({
                    # 'question': Question.objects.get(_id=note.question_id),
                    'id': question._id,
                    'title': question.title,
                    'difficulty': question.difficulty,
                    'note': note.question_note if note.question_note else '',
                })

            return render(request, 'punlum_new.html', {
                'punlum_items': punlum_items,
            })
        else:
            return HttpResponseRedirect('/account/login/')

    elif request.method == 'POST':
        question_id = request.POST.get('take_notes')
        notes_content = request.POST.get('notes_content' + question_id)
        print(notes_content)
        if notes_content:
            question = Question.objects.get(_id=question_id)
            note = request.user.punlum.notes.get(question_id=question_id)
            note.question_note = notes_content
            note.save()

        request.method = 'GET'
        return punlum_page(request)
