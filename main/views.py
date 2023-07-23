from django.shortcuts import render


def main_view(request):
    return render(request, 'test11.html')
    # return render(request, 'main.html')

