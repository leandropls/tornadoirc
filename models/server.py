# coding: utf-8

from typing import Undefined
from datetime import datetime
from settings import localtime


class Server(object):
    name = Undefined(str)
    date = Undefined(str)
    version = 'tornadoirc-0.0'
    usermodes = ''
    channelmodes = ''
    users = Undefined(dict)

    def __init__(self, name: str, date: str = str(datetime.now(localtime))):
        self.name = name
        self.date = date
        self.users = {}
