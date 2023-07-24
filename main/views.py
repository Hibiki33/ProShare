from django.shortcuts import render


def main_view(request):
    return render(request, 'main.html')
    # return render(request, 'abort_main.html')

def test_view(request):
    return render(request, 'problem_edit.html')
