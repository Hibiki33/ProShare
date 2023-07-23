from django.shortcuts import render


def main_view(request):
    return render(request, 'mainview.html')
    # return render(request, 'main.html')

