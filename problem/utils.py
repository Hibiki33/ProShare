import logging
from problem.models import Problem, Question


def list_msg(request,
             questions=Question.objects.all(),
             page=1, order='time',
             difficulty='all',
             type='all',
             uploader='all',
             search=''):

    # if request.method == 'GET':
    if difficulty != 'all':
        questions = questions.filter(difficulty=difficulty)
    if type != 'all':
        questions = questions.filter(type=type)
    if uploader != 'all':
        questions = questions.filter(created_by=uploader)
    if search != '':
        questions = questions.filter(title__contains=search)
    if order == 'time':
        questions = questions.order_by('-create_time')
    elif order == 'diff':
        questions = questions.order_by('difficulty')

    questions = questions[(page - 1) * 10: page * 10]

    msg = []
    for question in questions:
        msg.append({
            "ID": question._id,
            "Name": question.title,
            "Time": question.create_time,
            "Diff": question.difficulty,
        })
        tags = question.tags.all()
        for i in range(3):
            msg[-1][f'Tag{i + 1}'] = tags[i].name if len(tags) > i else ''
    logging.debug('problem_info_list: ')
    logging.info(msg)
    return msg


def detail_msg(request, id):
    if Question.objects.filter(_id=id).exists():
        question = Question.objects.get(_id=id)
        msg = {
            "ID": question._id,
            "Name": question.title,
            "Time": question.create_time,
            "Diff": question.difficulty,
            "Uploader": question.created_by,
            "Type": question.type,
            "Description": question.description,
            "Options": question.options,
            "Submit": question.submission_number,
            "Passed": question.passed_number,
        }
        logging.debug('problem detail: ')
        logging.info(msg)

        return msg
    elif Problem.objects.filter(_id=id).exists:
        problem = Problem.objects.get(_id=id)
        # TODO
        raise NotImplementedError
    else:
        raise FileNotFoundError
