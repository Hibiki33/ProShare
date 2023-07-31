
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

def downgrade(wei):
    from math import ceil, log2
    if wei <= 0:
        return 0
    return wei - max(int(ceil(pow(wei, 1 / 2))), int(log2(wei) + 1))
