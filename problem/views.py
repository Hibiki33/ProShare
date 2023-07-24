from django.shortcuts import render

# Create your views here.

def problem_lib_page(request):
    if request.method == 'GET':
        return render(request, 'problem_group_list.html')
    elif request.method == 'POST':
        pass

def detail(request, question_id):
    if request.method == 'GET':
        return render(request, 'problem_detail.html')
    elif request.method == 'POST':
        pass