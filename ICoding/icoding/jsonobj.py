#! /usr/bin/python
import json

import collections


class JsonObject(object):
    """
    >>> a = {
    ...     'a': {'aa': 1},
    ...     'b': [{'bb': 1}, {'bb': 2}, {'bb': 3}],
    ...    'c': {'cc': {'ccc': 111}},
    ... }
    >>> json_obj = JsonObject(a)
    >>> json_obj.b[0].bb
    1
    >>> json_obj.c.cc.cccx
    111
    """

    def __init__(self, value):
        self._value = value

    def __getattr__(self, item):
        if item not in self._value:
            raise AttributeError(
                '{0} has not attribute {1}'.format(self, item))
        obj = self._value[item]
        if isinstance(obj, dict):
            return JsonObject(obj)
        elif isinstance(obj, list):
            objs = []
            for s in obj:
                if isinstance(s, tuple([int, str])):
                    objs.append(s)
                else:
                    objs.append(JsonObject(s))
            return objs
        else:
            return obj

    def __getitem__(self, index):
        if isinstance(self.value, collections.Iterable):
            obj = self.value[index]
            if isinstance(obj, dict):
                return JsonObject(obj)
            else:
                return obj
        else:
            raise ValueError('{0} is not Iterable', self)

    def __repr__(self):
        return '<JsonObj keys={}>'.format(self.value.keys())


def loads(json_str):
    return JsonObject(json.loads(json_str))
