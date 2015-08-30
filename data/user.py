# coding: utf-8

from typing import Undefined, Optional
import logging

logger = logging.getLogger('tornado.general')

class User(object):
    nick = Undefined(str)
    hopcount = Undefined(int)
    username = Undefined(Optional[str])
    hostname = Undefined(Optional[str])
    servername = Undefined(Optional[str])
    realname = Undefined(Optional[str])
    registered = Undefined(bool)

    def __init__(self, nick: str, hopcount: int):
        self.nick = nick
        self.hopcount = hopcount
        self.hostname = None
        self.servername = None
        self.realname = None
        self.registered = False

    def register(self, username: str, hostname: str, servername: str,
                 realname: str):
        if self.registered:
            return

        self.username = username
        self.hostname = hostname
        self.servername = servername
        self.realname = realname
        self.registered = True

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)
