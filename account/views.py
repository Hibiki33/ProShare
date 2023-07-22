from .models import *
from django.shortcuts import render, redirect


def login_view(request):
    return render(request, 'login.html')


def login_page(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        login_name = request.POST.get('user_name')
        login_password = request.POST.get('user_password')

        if login_name is None or login_password is None:
            return render(request, 'login.html', {'message': 'user_name or password is empty!'})

        # TODO: This method may be unsafe
        if UserInfo.objects.filter(user_name=login_name, user_password=login_password).count() != 0:
            return redirect('main/')
        else:
            return render(request, 'login.html', {'message': 'user_name or password is wrong!'})

    return render(request, '404.html')


def register_view(request):
    return render(request, 'register.html')


def register_page(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_name = request.POST.get('user_name')
        user_password = request.POST.get('user_password')
        user_mail = request.POST.get('user_mail')
        user_phone = request.POST.get('user_phone')

        if user_id is None or user_name is None or user_password is None:
            return render(request, 'register.html', {'message': 'user_id, user_name and user_password is necessary!'})

        if UserInfo.objects.filter(user_id=user_id).count() != 0:
            return render(request, 'register.html', {'message': 'user_id is already exist!'})
        if UserInfo.objects.filter(user_name=user_name).count() != 0:
            return render(request, 'register.html', {'message': 'user_name is already exist!'})

    return redirect('main/')




