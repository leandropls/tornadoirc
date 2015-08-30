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
    connection = Undefined('Connection')
    registered = Undefined(bool)

    def __init__(self, nick: str, connection: 'Connection', hopcount: int):
        self.nick = nick
        self.hopcount = hopcount
        self.hostname = None
        self.servername = None
        self.realname = None
        self.connection = connection
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

        self.send_message('RPL_WELCOME',
                          nick = self.nick,
                          username = self.username,
                          hostname = self.hostname)

        self.send_message('RPL_YOURHOST',
                          servername = self.connection.server.name,
                          version = self.connection.server.version)

        self.send_message('RPL_CREATED',
                          date = self.connection.server.date)

        self.send_message('RPL_MYINFO',
                          servername = self.connection.server.name,
                          date = self.connection.server.date,
                          version = self.connection.server.version,
                          usermodes = self.connection.server.usermodes,
                          channelmodes = self.connection.server.channelmodes)

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)

    def send_message(self, *args, **kwargs):
        self.connection.send_message(*args,
                                     msgfrom = self.connection.server.name,
                                     msgto = self.nick,
                                     **kwargs)
