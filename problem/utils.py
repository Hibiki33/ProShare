import logging
from problem.models import Problem, Question, ProblemFile, QuestionTag
from ProShare.settings import MEDIA_ROOT
import os
import re


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
    

def exist_tag(tag_name):
    return QuestionTag.objects.filter(name=tag_name).exists()


def parse_file(file):

    if file is None:
        raise Exception('No File Uploaded!')
    
    if not os.path.exists(MEDIA_ROOT / file.name):
        raise Exception('File not found!')

    # ProblemFile.objects.create(file_name=file.name,
    #                            file=file)

    problems = []
    with open(MEDIA_ROOT / file.name, 'r+', encoding='utf-8') as source:
        line = source.readline()
        line_cnt = 1
        status = 0
        problem = {}
        while line:
            if line.startswith('Title'):
                if status != 0:
                    raise Exception('Error at %d: Unexpected Title' % line_cnt)
                _, title = line.split(':')
                title = title.strip()
                problem['title'] = title
                status = 1

            elif line.startswith('Description'):
                if status != 1:
                    raise Exception('Error at %d: Unexpected Description' % line_cnt)
                _, description = line.split(':')
                description = description.strip()
                problem['description'] = description
                status = 2

            elif line.startswith('Difficulty'):
                if status != 2:
                    raise Exception('Error at %d: Unexpected Difficulty' % line_cnt)
                _, difficulty = line.split(':')
                difficulty = difficulty.strip()
                if difficulty not in ['0', '1', '2', '3', '4', '5']:
                    raise Exception('Error at %d: Invalid Difficulty' % line_cnt)
                problem['difficulty'] = difficulty
                status = 3

            elif line.startswith('Type'):
                if status != 3:
                    raise Exception('Error at %d: Unexpected Type' % line_cnt)
                _, _type = line.split(':')
                _type = _type.strip()
                if _type not in ['0', '1', '2']:
                    raise Exception('Error at %d: Invalid Type' % line_cnt)
                problem['type'] = _type

                if _type == '0' or _type == '1':
                    line = source.readline()
                    if not line.startswith('Options'):
                        raise Exception('Error at %d: Unexpected Options' % line_cnt)
                    # options = list(line.split())
                    _, options = line.split(':')
                    options = list(re.split(r'A.|B.|C.|D.|:', options))
                    options = options[1:]
                    print(options)
                    # print('1', end='')
                    # print(options)

                    problem['options'] = options
                status = 4

            elif line.startswith('Answer'):
                if status != 4:
                    raise Exception('Error at %d: Unexpected Answer' % line_cnt)
                _, answer = line.split(':')
                answer = answer.strip()
                problem['answer'] = answer
                status = 5

            elif line.startswith('Tags'):
                if status != 5:
                    raise Exception('Error at %d: Unexpected Tag' % line_cnt)
                _, tags = line.split(':')
                tags = [x.strip() for x in tags.split()]
                # for tag in tags:
                #     if not exist_tag(tag):
                #         raise Exception('Error at %d: Invalid Tag' % line_cnt)
                problem['tags'] = tags
                problems.append(problem)
                problem = {}
                line = source.readline()
                line_cnt += 1

            line = source.readline()
            line_cnt += 1

    logging.debug('uploaded problems: ')
    logging.info(problems)

    return problems


def new_tag(tagname):
    QuestionTag.objects.create(name=tagname)