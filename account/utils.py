from math import log2

from django.contrib.auth import get_user_model
from problem.models import Question, QuestionTag
User = get_user_model()


def gen_ability_map(user, lack=False):
    wrong_questions = user.get_wrong_questions()
    related_ability = [0, 0, 0, 0, 0, 0]

    for q in wrong_questions:
        tags = q.tags.all()
        for tag in tags:
            related_ability[tag.ability] += 1

    if lack:
        user_lack_ability = related_ability

        total_ability = 0
        for i in user_lack_ability:
            total_ability += i
        total_ability += 0.2
        user_ability = [2**((total_ability - i) / total_ability) - 1 for i in user_lack_ability]

        return user_ability

    return related_ability
