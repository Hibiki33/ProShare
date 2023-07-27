import logging
from problem.models import Problem, Question


def list_msg(request, page=1, order='time', difficulty='all', type='all', uploader='all', search=''):
    if request.method == 'GET':
        questions = Question.objects.all()
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
                "Tag1": question.tags[0].name,
                "Tag2": question.tags[1].name,
                "Tag3": question.tags[2].name,
            })
        logging.debug('problem_info_list: ')
        logging.info(msg)
        return msg
    elif request.method == 'POST':
        pass


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
