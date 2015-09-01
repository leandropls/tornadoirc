# coding: utf-8

from typing import Undefined, Tuple
import logging

logger = logging.getLogger('tornado.general')

class EntityRouter(object):
    '''Provides simple interface to find users and channels.'''
    paths = Undefined(Tuple[Tuple[str, dict]])
    # paths = [('', users), ('#', channels)]

    def __init__(self, *paths: Tuple[Tuple[str, dict]]):
        self.paths = dict(paths)

    def __contains__(self, name: str):
        prefix = name[0]
        if prefix in self.paths:
            return name in self.paths[prefix]
        return name in self.paths['']

    def __getitem__(self, name: str):
        prefix = name[0]
        if prefix in self.paths:
            return self.paths[prefix][name]
        return self.paths[''][name]
