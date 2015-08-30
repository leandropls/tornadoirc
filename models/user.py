# coding: utf-8

from models.server import Server
from models.exceptions import *
import settings

from typing import Undefined, Optional
import logging
import re

logger = logging.getLogger('tornado.general')

class User(object):
    _nick = Undefined(Optional[str])
    hopcount = Undefined(int)
    username = Undefined(Optional[str])
    hostname = Undefined(Optional[str])
    servername = Undefined(Optional[str])
    realname = Undefined(Optional[str])
    connection = Undefined('Connection')
    server = Undefined(Server)
    registered = Undefined(bool)

    _nick_regex = re.compile(r'(\w+)')

    @property
    def nick(self):
        return self._nick

    @nick.setter
    def nick(self, value):
        '''Validate and set nick value.'''
        match = self._nick_regex.match(value)
        if not match:
            raise ErroneousNicknameError(value)
        value = match.groups()[0]

        nicklen = settings.user['nicklen']
        value = value[0 : min(len(value), nicklen)]

        if value in self.server.users:
            raise NicknameInUseError(value)

        self._nick = value

    def __init__(self, nick: str, connection: 'Connection', server: Server,
                 hopcount: int):
        self.connection = connection
        self.server = server
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

        self.send_message('RPL_WELCOME',
                          nick = self.nick,
                          username = self.username,
                          hostname = self.hostname)

        self.send_message('RPL_YOURHOST',
                          servername = self.server.name,
                          version = self.server.version)

        self.send_message('RPL_CREATED',
                          date = self.server.date)

        self.send_message('RPL_MYINFO',
                          servername = self.server.name,
                          date = self.server.date,
                          version = self.server.version,
                          usermodes = self.server.usermodes,
                          channelmodes = self.server.channelmodes)

        self.cmd_motd(None)

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)

    def send_message(self, *args, **kwargs):
        '''Send message to user.'''
        self.connection.send_message(*args,
                                     msgfrom = self.server.name,
                                     msgto = self.nick,
                                     **kwargs)

    def cmd_motd(self, prefix: Optional[str], target: Optional[str] = None):
        '''Process MOTD command.'''
        if not settings.ircd['motd']:
            raise NoMotdError()
        self.send_message('RPL_MOTDSTART', servername = self.server.name)
        for text in settings.ircd['motd']:
            self.send_message('RPL_MOTD', text = text)
        self.send_message('RPL_ENDOFMOTD')

    def cmd_ping(self, prefix: Optional[str], payload: str,
        destination: Optional[str] = None):
        '''Process PING command.'''
        if destination and destination != self.server.name:
            raise NoSuchServerError(servername = destination)
        self.send_message('CMD_PONG', payload = payload)
