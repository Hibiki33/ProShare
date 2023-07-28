from django.shortcuts import render
from problem.utils import list_msg


def main_view(request):
    return render(request, 'main.html', {'problem_info_list': list_msg(request)})
    # return render(request, 'abort_main.html')


def test_view(request):
    return render(request, 'problem_set_findadd.html')


def not_found_view(request):
    return render(request, '404.html')
