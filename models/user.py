# coding: utf-8

from models.server import Server
from models.exceptions import *

from tornado.ioloop import IOLoop

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
    timeouttimer = None

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

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)

    def closed(self):
        if self.pingtimer:
            self.pingtimer.stop()
        if self.timeouttimer:
            self.timeouttimer.stop()

    ##
    # Server send msg commands
    ##
    def send_message(self, *args, **kwargs):
        '''Send message to user.'''
        self.connection.send_message(*args, **kwargs)

    def send_ping(self):
        '''Send PING to user'''
        if self.connection.stream.closed():
            return
        io_loop = IOLoop.current()
        self.pingtimer = io_loop.call_later(
                            self.server.settings['pinginterval'],
                            self.send_ping)
        self.timeouttimer = io_loop.call_later(
                                self.server.settings['pingtimeout'],
                                self.timeout)
        self.send_message('CMD_PING')

    def timeout(self):
        '''Disconnect user for timeout.'''
        self.send_message('CMD_ERROR', text = 'Ping timeout')
        if not self.connection.stream.closed():
            self.connection.stream.close()

    def send_welcome(self):
        '''Send welcome messages to user.'''
        self.send_message('RPL_WELCOME')
        self.send_message('RPL_YOURHOST', version = self.server.version)
        self.send_message('RPL_CREATED', date = self.server.date)
        self.send_message('RPL_MYINFO',
                          date = self.server.date,
                          version = self.server.version,
                          usermodes = self.server.usermodes,
                          channelmodes = self.server.channelmodes)

        self.cmd_motd(None)
        self.send_ping()

    def send_privmsg(self, origin: str, text: str):
        '''Send PRIVMSG command to user.'''
        self.send_message('CMD_PRIVMSG',
                          originaddr = origin.address,
                          text = text)

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

    def cmd_pong(self, prefix: Optional[str], payload: str):
        IOLoop.current().remove_timeout(self.timeouttimer)
        self.timeouttimer = None

    def cmd_nick(self, prefix: Optional[str], nick: str):
        '''Process NICK command.'''
        oldaddr = self.address
        oldnick = self.nick
        self.nick = nick
        if self.nick != oldnick:
            self.server.users[self.nick] = self
            del self.server.users[oldnick]

        self.send_message('CMD_NICK', oldaddr = oldaddr, nick = self.nick)

    def cmd_privmsg(self, prefix: Optional[str], target: str, text: str):
        '''Process PRIVMSG command.'''
        if target not in self.server.users:
            raise NoSuchNickError(nick = target)
        target_user = self.server.users[target]
        target_user.send_privmsg(origin = self, text = text)
