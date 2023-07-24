from django.shortcuts import render

# Create your views here.

def question_lib_page(request):
    if request.method == 'GET':
        return render(request, 'question_lib.html')
    elif request.method == 'POST':
        pass
