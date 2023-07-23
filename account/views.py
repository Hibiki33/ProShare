from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import uuid


def get_uuid(length=8):
    return str(uuid.uuid4()).replace('-', '')[:length]


def login_view(request):
    return render(request, 'newlogin.html')


def login_page(request):
    if request.method == 'GET':
        return render(request, 'newlogin.html')
    elif request.method == 'POST':
        login_name = request.POST.get('username', '')
        login_password = request.POST.get('password', '')
        print(login_name, login_password)
        if not login_name or not login_password:
            # return render(request, 'login.html', {'message': 'user_name or password is empty!'})
            messages.error(request, 'user_name or password is empty!')
            return HttpResponseRedirect('/account/login/')

        # TODO: This method may be unsafe
        if UserInfo.objects.filter(user_name=login_name, user_password=login_password).count() != 0:
            return redirect('../../')
        else:
            # return render(request, 'login.html', {'message': 'user_name or password is wrong!'})
            messages.error(request, 'user_name or password is wrong!')
            return HttpResponseRedirect('/account/login/')

    return render(request, '404.html')


def register_view(request):
    return render(request, 'newregister.html')


def register_page(request):
    if request.method == 'GET':
        return render(request, 'newregister.html')
    elif request.method == 'POST':
        user_id = get_uuid()
        user_name = request.POST.get('username', '')
        user_password = request.POST.get('password', '')
        user_confirm_password = request.POST.get('confirm_password', '')
        user_mail = request.POST.get('email', '')
        user_phone = request.POST.get('tel', '')

        if user_password != user_confirm_password:
            # return render(request, 'register.html', {'message': 'password and confirm_password is not same!'})
            messages.error(request, 'password and confirm_password is not same!')
            return HttpResponseRedirect('/account/register/')

        if not user_name or not user_password:
            # return render(request, 'register.html', {'message': 'name and password is necessary!'})
            messages.error(request, 'name and password is necessary!')
            return HttpResponseRedirect('/account/register/')

        if UserInfo.objects.filter(user_name=user_name).count() != 0:
            # return render(request, 'register.html', {'message': 'user_name is already exist!'})
            messages.error(request, 'user_name is already exist!')
            return HttpResponseRedirect('/account/register/')

        UserInfo.objects.create(user_id=int(user_id, 16),
                                user_name=user_name,
                                user_password=user_password,
                                user_mail=user_mail,
                                user_phone=user_phone)
        return redirect('../../')

    return render(request, '404.html')


def change_pwd_view(request):
    return render(request, 'changePasswd.html')

def edit_view(request):
    return render(request, 'homeEdit.html')


def main_view(request):
    return render(request, 'home.html')
