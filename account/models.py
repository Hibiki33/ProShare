from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

from utils.models import RichTextField, JSONField


# class UserInfo(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     user_name = models.CharField(max_length=20)
#     user_password = models.CharField(max_length=20)
#     user_mail = models.CharField(max_length=20)
#     user_phone = models.CharField(max_length=20)
#
#     user_quote = models.CharField(max_length=128)


class UserManager(BaseUserManager):
    def _create_user(self, username, password, email, **extra_fields):
        if not username:
            raise ValueError('Username must be set!')
        if not password:
            raise ValueError('Password must be set!')
        if not email:
            raise ValueError('Email must be set!')

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, password, **extra_fields):
        extra_fields['is_superuser'] = False
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields['is_superuser'] = True
        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    phone = RichTextField(max_length=11, null=True, blank=True)
    quote = models.TextField(max_length=128, null=True, blank=True)

    wrong_problems = models.ManyToManyField("problem.Problem", blank=True)
    wrong_questions = models.ManyToManyField("problem.Question", blank=True)

    finish_questions_cnt = models.IntegerField(default=0)
    wrong_questions_cnt = models.IntegerField(default=0)

    def set_quote(self, quote):
        self.quote = quote
        self.save()

    def set_phone(self, phone):
        self.phone = phone
        self.save()

    def get_quote(self):
        return self.quote

    def get_phone(self):
        return self.phone

    def add_wrong_question(self, question):
        self.wrong_questions.add(question)
        for tag in question.tags.all():
            self.tag_count[tag.name] = self.tag_count.get(tag.name, 0) + 2
        self.memorization_recommendation = True
        self.save()

    def add_wrong_problem(self, problem):
        self.wrong_problems.add(problem)
        self.save()

    def remove_wrong_question(self, question):
        if self.is_wrong_question(question):
            self.wrong_questions.remove(question)
            for tag in question.tags.all():
                self.tag_count[tag.name] = self.tag_count.get(tag.name, 1) - 1
                if self.tag_count[tag.name] == 0:
                    del self.tag_count[tag.name]
            self.memorization_recommendation = True
            self.save()

    def remove_wrong_problem(self, problem):
        if self.is_wrong_problem(problem):
            self.wrong_problems.remove(problem)
            self.save()

    def get_wrong_questions(self):
        return self.wrong_questions.all()

    def get_wrong_problems(self):
        return self.wrong_problems.all()

    def is_wrong_question(self, question):
        return question in self.wrong_questions.all()

    def is_wrong_problem(self, problem):
        return problem in self.wrong_problems.all()

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    recommended_questions = models.ManyToManyField(
        "problem.Question", blank=True, related_name="recommended")
    tag_count = JSONField(default=dict)
    memorization_recommendation = models.BooleanField(default=True)

    def get_recommended_questions(self):
        class Recommendation:
            def __init__(self, iterable=[], _load=200):
                values = sorted(iterable)
                self._len = _len = len(values)
                self._load = _load
                self._lists = _lists = [values[i:i + _load]
                                        for i in range(0, _len, _load)]
                self._list_lens = [len(_list) for _list in _lists]
                self._mins = [_list[0] for _list in _lists]
                self._reco_tree = []
                self._rebuild = True

            def _reco_build(self):
                self._reco_tree[:] = self._list_lens
                _reco_tree = self._reco_tree
                for i in range(len(_reco_tree)):
                    if i | i + 1 < len(_reco_tree):
                        _reco_tree[i | i + 1] += _reco_tree[i]
                self._rebuild = False

            def _reco_update(self, index, value):
                if not self._rebuild:
                    _reco_tree = self._reco_tree
                    while index < len(_reco_tree):
                        _reco_tree[index] += value
                        index |= index + 1

            def _reco_query(self, end):
                if self._rebuild:
                    self._reco_build()
                _reco_tree = self._reco_tree
                x = 0
                while end:
                    x += _reco_tree[end - 1]
                    end &= end - 1
                return x

            def _reco_findkth(self, k):
                _list_lens = self._list_lens
                if k < _list_lens[0]:
                    return 0, k
                if k >= self._len - _list_lens[-1]:
                    return len(_list_lens) - 1, k + _list_lens[-1] - self._len
                if self._rebuild:
                    self._reco_build()
                _reco_tree = self._reco_tree
                idx = -1
                for d in reversed(range(len(_reco_tree).bit_length())):
                    right_idx = idx + (1 << d)
                    if right_idx < len(_reco_tree) and k >= _reco_tree[right_idx]:
                        idx = right_idx
                        k -= _reco_tree[idx]
                return idx + 1, k

            def _delete(self, pos, idx):
                _lists, _mins, _list_lens = self._lists, self._mins, self._list_lens
                self._len -= 1
                self._reco_update(pos, -1)
                del _lists[pos][idx]
                _list_lens[pos] -= 1
                if _list_lens[pos]:
                    _mins[pos] = _lists[pos][0]
                else:
                    del _lists[pos]
                    del _list_lens[pos]
                    del _mins[pos]
                    self._rebuild = True

            def _loc_left(self, value):
                if not self._len:
                    return 0, 0
                _lists = self._lists
                _mins = self._mins
                lo, pos = -1, len(_lists) - 1
                while lo + 1 < pos:
                    mi = (lo + pos) >> 1
                    (lo, pos) = (mi, pos) if _mins[mi] < value else (lo, mi)
                if pos and value <= _lists[pos - 1][-1]:
                    pos -= 1
                _list = _lists[pos]
                lo, idx = -1, len(_list)
                while lo + 1 < idx:
                    mi = (lo + idx) >> 1
                    (lo, idx) = (mi, idx) if _list[mi] < value else (lo, mi)
                return pos, idx

            def _loc_right(self, value):
                if not self._len:
                    return 0, 0
                _lists = self._lists
                _mins = self._mins
                pos, hi = 0, len(_lists)
                while pos + 1 < hi:
                    mi = (pos + hi) >> 1
                    (pos, hi) = (mi, hi) if _mins[mi] <= value else (pos, mi)
                _list = _lists[pos]
                lo, idx = -1, len(_list)
                while lo + 1 < idx:
                    mi = (lo + idx) >> 1
                    (lo, idx) = (mi, idx) if _list[mi] <= value else (lo, mi)
                return pos, idx

            def add(self, value):
                """Add `value` to sorted list."""
                _load = self._load
                _lists = self._lists
                _mins = self._mins
                _list_lens = self._list_lens
                self._len += 1
                if _lists:
                    pos, idx = self._loc_right(value)
                    self._reco_update(pos, 1)
                    _list = _lists[pos]
                    _list.insert(idx, value)
                    _list_lens[pos] += 1
                    _mins[pos] = _list[0]
                    if _load + _load < len(_list):
                        _lists.insert(pos + 1, _list[_load:])
                        _list_lens.insert(pos + 1, len(_list) - _load)
                        _mins.insert(pos + 1, _list[_load])
                        _list_lens[pos] = _load
                        del _list[_load:]
                        self._rebuild = True
                else:
                    _lists.append([value])
                    _mins.append(value)
                    _list_lens.append(1)
                    self._rebuild = True

            def discard(self, value):
                _lists = self._lists
                if _lists:
                    pos, idx = self._loc_right(value)
                    if idx and _lists[pos][idx - 1] == value:
                        self._delete(pos, idx - 1)

            def remove(self, value):
                _len = self._len
                self.discard(value)
                if _len == self._len:
                    raise ValueError('{0!r} not in list'.format(value))

            def pop(self, index=-1):
                pos, idx = self._reco_findkth(
                    self._len + index if index < 0 else index)
                value = self._lists[pos][idx]
                self._delete(pos, idx)
                return value

            def bisect_left(self, value):
                pos, idx = self._loc_left(value)
                return self._reco_query(pos) + idx

            def bisect_right(self, value):
                pos, idx = self._loc_right(value)
                return self._reco_query(pos) + idx

            def count(self, value):
                return self.bisect_right(value) - self.bisect_left(value)

            def __len__(self):
                return self._len

            def __getitem__(self, index):
                pos, idx = self._reco_findkth(
                    self._len + index if index < 0 else index)
                return self._lists[pos][idx]

            def __delitem__(self, index):
                pos, idx = self._reco_findkth(
                    self._len + index if index < 0 else index)
                self._delete(pos, idx)

            def __contains__(self, value):
                _lists = self._lists
                if _lists:
                    pos, idx = self._loc_left(value)
                    return idx < len(_lists[pos]) and _lists[pos][idx] == value
                return False

            def __iter__(self):
                return (value for _list in self._lists for value in _list)

            def __reversed__(self):
                return (value for _list in reversed(self._lists) for value in reversed(_list))

            def __repr__(self):
                return f'Recommendation({list(self)})'

        def downgrade(wei):
            from math import ceil, log2
            if wei <= 0:
                return 0
            return wei - max(int(ceil(pow(wei, 1 / 2))), int(log2(wei) + 1))

        from problem.models import QuestionTag
        if self.memorization_recommendation:
            q = {}
            for tag in self.tag_count:
                for question in QuestionTag.objects.get(name=tag).questions.all():
                    q[question._id] = (q.get(question.id, 0)[0] + 1, question)
            for question in self.get_wrong_questions():
                q[question._id] = downgrade(q.get(question._id, 0))
            reco = Recommendation()
            for question in q.values():
                reco.add(question)
            self.recommended_questions.clear()
            for _ in range(min(10, len(reco))):
                self.recommended_questions.add(reco.pop())
        return self.recommended_questions.all()


class Punlum(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='punlum')


class PunlumNote(models.Model):
    question_id = models.IntegerField()
    question_note = models.TextField(max_length=1024, null=True, blank=True)

    punlum = models.ForeignKey(
        Punlum, on_delete=models.CASCADE, related_name="notes")
