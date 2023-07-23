from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user_model
import uuid

User = get_user_model()


def get_uuid(length=8):
    return str(uuid.uuid4()).replace('-', '')[:length]


def login_view(request):
    return render(request, 'login.html')


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

        if user and user.is_active:
            login(request, user)
            request.session['username'] = username
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Username or Password is wrong!')
            return HttpResponseRedirect('/account/login/')

    return render(request, '404.html')


def register_view(request):
    return render(request, 'register.html')


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
            messages.error(request, 'password and confirm_password is not same!')
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

        User.objects.create(username=username,
                            password=password,
                            email=email)
        return HttpResponseRedirect('/account/')

    return render(request, '404.html')


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


def change_pwd_view(request):
    return render(request, 'change_password.html')


def edit_view(request):
    return render(request, 'home_edit.html')


def main_view(request):
    return render(request, 'home.html')
