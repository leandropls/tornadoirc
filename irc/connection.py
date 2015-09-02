# coding: utf-8

from .user import User
from .messages import messages
from .exceptions import *

from tornado.iostream import IOStream
from tornado.ioloop import IOLoop

from typing import Undefined, List, Optional, Callable
import logging
import inspect
import time

logger = logging.getLogger('tornado.general')

class Connection(object):
    stream = Undefined(IOStream)
    address = Undefined(str)
    port = Undefined(int)
    server = Undefined('Server')
    password = Undefined(Optional[str])
    user = Undefined(Optional[User])
    req_user = None
    req_nick = None
    regtimer = None

    def __init__(self, stream: IOStream, server: 'Server',
                 address: str, port: int):
        self.stream = stream
        self.address = address
        self.port = port
        self.server = server
        self.password = None
        self.user = None

        # Set timeout for registering
        self.regtimer = IOLoop.current().call_later(
                            self.server.settings['pingtimeout'],
                            self.stream.close)

    ##
    # Events
    ##
    def on_read(self, prefix: str, command: str, params: List[str]):
        '''Process message received from connection.'''
        # Created method name
        methodname = 'cmd_%s' % command.lower()

        # Process command
        t0 = time.monotonic()
        try:
            if self.user and hasattr(self.user, methodname):
                self._call_user_method(command, params)
            elif hasattr(self, methodname):
                self._call_conn_method(prefix, command, params)
        except CommandError as e:
            self.send_message(msgid = e.msgid, **e.msgparams)
        finally:
            t1 = time.monotonic()
            elapsed = format((t1 - t0) * 1e3, '.2f')
            client = (self.user.address
                     if self.user
                     else '%s:%s' % (self.address, self.port))
            logger.info('%s %s %sms', client, command.upper(), elapsed)

    def on_close(self):
        '''Deals with a connection closed event.'''
        if self.user:
            self.user.on_close()

    ##
    # Server initiated actions
    ##
    def send_message(self, msgid: str, **params):
        '''Send message to connection.'''
        if self.stream.closed():
            return
        params['servername'] = self.server.name
        params['target'] = self.user.nick if self.user else '*'
        params['targetaddr'] = self.user.address if self.user else '*'
        params['ipaddr'] = self.address

        message = messages[msgid] % params + '\r\n'
        message = message.encode('utf-8')
        if len(message) > 512:
            raise TooLongMessageException(length = len(message))
        self.stream.write(message)

    def register_user(self):
        '''Creates new user and adds it to server user\'s list.'''
        if not self.req_nick or not self.req_user:
            return

        if self.user:
            raise AlreadyRegisteredError()

        self.user = User(nick = self.req_nick, server = self.server,
                         connection = self, hopcount = 0,
                         username = '~' + self.req_user['username'],
                         hostname = self.address,
                         servername = self.server.name,
                         realname = self.req_user['realname'])
        self.req_nick = None
        self.req_user = None
        self.server.users[self.user.nick] = self.user

        # Remove register timeout timer
        if self.regtimer:
            IOLoop.current().remove_timeout(self.regtimer)
            self.regtimer = None

        # Call user on_register event
        self.user.on_register()

    ##
    # Command processing auxiliary methods
    ##
    def _call_conn_method(self, prefix: str, command: str, params: list):
        '''Process command by calling method on Connection.'''
        methodname = 'cmd_%s' % command.lower()
        method = getattr(self, methodname)

        # Check method args
        args, varargs, _, defaults, _, _, _ = inspect.getfullargspec(method)
        argnum = len(args) if args else 0
        defnum = len(defaults) if defaults else 0

        # Check if we have enough parameters to call method
        if len(params) < argnum - defnum - 2:
            raise NeedMoreParamsError(command = command.upper())

        # Call method
        if not varargs:
            method(prefix, *params[0 : argnum - 2])
        else:
            method(prefix, *params)

    def _call_user_method(self, command: str, params: list):
        '''Process command by calling method on User.'''
        methodname = 'cmd_%s' % command.lower()
        method = getattr(self.user, methodname)

        # Check method args
        args, varargs, _, defaults, _, _, _ = inspect.getfullargspec(method)
        argnum = len(args) if args else 0
        defnum = len(defaults) if defaults else 0

        # Check if we have enough parameters to call method
        if len(params) < argnum - defnum - 1:
            raise NeedMoreParamsError(command = command.upper())

        # Call method
        if not varargs:
            method(*params[0 : argnum - 1])
        else:
            method(*params)

    ##
    # User initiated actions
    ##
    def cmd_nick(self, prefix: Optional[str], nick: Optional[str] = None):
        '''Process NICK command.'''
        if not nick:
            raise NoNicknameGivenError()
        self.req_nick = nick
        self.register_user()

    def cmd_user(self, prefix: Optional[str],
                 username: str, mode: str, unused: str, realname: str):
        '''Process USER command.'''
        self.req_user = {'username': username, 'mode': mode,
                         'realname': realname}
        self.register_user()
