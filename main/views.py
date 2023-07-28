from django.shortcuts import render
from problem.utils import list_msg


def main_view(request):
    return render(request, 'main.html', {'problem_info_list': list_msg(request)})
    # return render(request, 'abort_main.html')


def test_view(request):
    # a = [
    #     {"ID": 1, "Name": "Question A", "Diff": "Easy", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"},
    #     {"ID": 2, "Name": "Question B", "Diff": "Medium", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"},
    #     {"ID": 3, "Name": "Question C", "Diff": "Hard", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"},
    #     {"ID": 4, "Name": "Question D", "Diff": "Easy", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"},
    #     {"ID": 5, "Name": "Question E", "Diff": "Medium", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"},
    #     {"ID": 6, "Name": "Question F", "Diff": "Hard", "Tag1": "Tag1", "Tag2": "Tag2", "Tag3": "Tag3"}
    # ]
    # return render(request, 'problem_set_findadd.html', {"problem_info_list": a})
    a = [
        {"id": 1, "name": "Question A", "created_by": "Easy", "belongs_to": "Tag1"},
        {"id": 2, "name": "Question B", "created_by": "Medium", "belongs_to": "Tag1"},
        {"id": 3, "name": "Question C", "created_by": "Hard", "belongs_to": "Tag1"},
        {"id": 4, "name": "Question D", "created_by": "Easy", "belongs_to": "Tag1"},
    ]
    return render(request, 'problem_set_list.html', {"problem_set_list": a})


def not_found_view(request):
    return render(request, '404.html')
