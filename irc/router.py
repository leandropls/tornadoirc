# coding: utf-8

from typing import Undefined, Tuple

class EntityRouter(object):
    '''Provides simple interface to find users and channels.'''
    paths = Undefined(Tuple[Tuple[str, dict]])
    # paths = [('', users), ('#', channels)]

    def __init__(self, *paths: Tuple[Tuple[str, dict]]):
        self.paths = paths

    def __contains__(self, name: str):
        for prefix, catalog in self.paths:
            if prefix and name[0] == prefix:
                sname = name[1:]
                if sname in catalog:
                    return True
                return False
            elif not prefix:
                if name in catalog:
                    return True
                return False
        return False

    def __getitem__(self, name: str):
        for prefix, catalog in self.paths:
            if prefix and name[0] == prefix:
                sname = name[1:]
                if sname in catalog:
                    return catalog[sname]
                raise KeyError(name)
            elif not prefix:
                if name in catalog:
                    return catalog[name]
                raise KeyError(name)
        raise KeyError(name)
