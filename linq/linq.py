
from collections import defaultdict

class linq:
    def __init__(self, iterable):
        self.iterable = iterable

    def __iter__(self):
        return self.iterable.__iter__()

    def Select(self, func):
        return linq(map(func, self.iterable))

    def Flatten(self):

        def gen(iterable):
            for array in iterable:
                for elem in array:
                    yield elem

        return linq(gen(self.iterable))

    def Where(self, _filter):
        return linq(filter(_filter, self.iterable))

    def Take(self, n):

        def gen(iterable, n):
            i = 0
            for elem in iterable:
                if i == n:
                    break
                yield elem
                i += 1

        return linq(gen(self.iterable, n))

    def GroupBy(self, func):

        _dict = defaultdict(list)

        for elem in self.iterable:
            _dict[func(elem)].append(elem)

        return linq(_dict.items())

    def OrderBy(self, func):
        return linq(sorted(self.iterable, key=func))

    def ToList(self):
        return list(self.iterable)

    def next(self):
        return self.iterable.next()
