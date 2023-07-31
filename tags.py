from problem.utils import new_tag

with open('tags.txt', 'r', encoding='utf-8') as source:
    line = source.readline()
    while line:
        line = line.strip()
        new_tag(line)
        line = source.readline()