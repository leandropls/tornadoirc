# coding: utf-8

from models.server import Server
from models.exceptions import *

from tornado.ioloop import PeriodicCallback

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
    pingtimer = None

    ##
    # Nick getter and setter
    ##
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

        nicklen = self.server.settings['nicklen']
        value = value[0 : min(len(value), nicklen)]

        if value == self._nick:
            return

        if value in self.server.users:
            raise NicknameInUseError(value)

        self._nick = value

    @property
    def address(self):
        return '%s!%s@%s' % (self.nick, self.username, self.hostname)

    ##
    # Init
    ##
    def __init__(self, nick: str, connection: 'Connection', server: Server,
                 hopcount: int, username: str, hostname: str, servername: str,
                 realname: str):
        self.connection = connection
        self.server = server
        self.nick = nick
        self.hopcount = hopcount
        self.username = username
        self.hostname = hostname
        self.servername = servername
        self.realname = realname

        self.pingtimer = PeriodicCallback(self.send_ping,
            int(self.server.settings['pinginterval'] * 1e3))
        self.pingtimer.start()

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)

    def closed(self):
        if self.pingtimer:
            self.pingtimer.stop()

    ##
    # Server send msg commands
    ##
    def send_message(self, *args, **kwargs):
        '''Send message to user.'''
        self.connection.send_message(*args, **kwargs)

    def send_ping(self):
        '''Send PING to user'''
        message = 'PING :%s\r\n' % self.server.name
        message = message.encode('utf-8')
        self.connection.stream.write(message)

    def send_welcome(self):
        self.send_message('RPL_WELCOME')
        self.send_message('RPL_YOURHOST', version = self.server.version)
        self.send_message('RPL_CREATED', date = self.server.date)
        self.send_message('RPL_MYINFO',
                          date = self.server.date,
                          version = self.server.version,
                          usermodes = self.server.usermodes,
                          channelmodes = self.server.channelmodes)

        self.cmd_motd(None)

    ##
    # Server command handlers
    ##
    def cmd_motd(self, prefix: Optional[str], target: Optional[str] = None):
        '''Process MOTD command.'''
        if not self.server.settings['motd']:
            raise NoMotdError()
        self.send_message('RPL_MOTDSTART')
        for text in self.server.settings['motd']:
            self.send_message('RPL_MOTD', text = text[0 : min(len(text) + 1, 81)])
        self.send_message('RPL_ENDOFMOTD')

    def cmd_ping(self, prefix: Optional[str], payload: str,
        destination: Optional[str] = None):
        '''Process PING command.'''
        if destination and destination != self.server.name:
            raise NoSuchServerError(servername = destination)
        self.send_message('CMD_PONG', payload = payload)

    def cmd_nick(self, prefix: Optional[str], nick: str):
        '''Process NICK command.'''
        oldaddr = self.address
        oldnick = self.nick
        self.nick = nick
        if self.nick != oldnick:
            self.server.users[self.nick] = self
            del self.server.users[oldnick]

        self.send_message('CMD_NICK', oldaddr = oldaddr, nick = self.nick)
