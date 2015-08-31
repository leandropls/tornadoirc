# coding: utf-8

from models.user import User
from models.messages import messages
from models.exceptions import *

from tornado.iostream import IOStream

from typing import Undefined, List, Optional
import logging
import inspect

logger = logging.getLogger('tornado.general')

class Connection(object):
    stream = Undefined(IOStream)
    address = Undefined(str)
    port = Undefined(int)
    server = Undefined('Server')
    password = Undefined(Optional[str])
    user = Undefined(Optional[User])

    def __init__(self, stream: IOStream, server: 'Server',
                 address: str, port: int):
        self.stream = stream
        self.address = address
        self.port = port
        self.server = server
        self.password = None
        self.user = None
        self.req_user = None
        self.req_nick = None

    def send_message(self, msgid: str, sender: Optional[str] = None, **params):
        '''Send message to connection.'''
        params['servername'] = self.server.name
        params['target'] = self.user.nick if self.user else '*'
        params['targetaddr'] = self.user.address if self.user else '*'

        message = messages[msgid] % params + '\r\n'
        message = message.encode('utf-8')
        self.stream.write(message)

    def on_read(self, prefix: str, command: str, params: List[str]):
        '''Process message received from connection.'''
        # Created method name
        methodname = 'cmd_%s' % command

        # Check if method exists and fetch it if it does
        method = None
        if self.user:
            if hasattr(self.user, methodname):
                method = getattr(self.user, methodname)
        if not method:
            if not hasattr(self, methodname):
                return
            method = getattr(self, methodname)

        # Process command
        try:
            # Check method args
            args, _, _, defaults, _, _, _ = inspect.getfullargspec(method)
            argnum = len(args) if args else 0
            defnum = len(defaults) if defaults else 0

            # Check if we have enough parameters to call method
            if len(params) < argnum - defnum - 2:
                raise NeedMoreParamsError(command = command.upper())

            # Call method
            method(prefix, *params[0 : argnum - 2])
        except CommandError as e:
            self.send_message(msgid = e.msgid, **e.msgparams)

    def cmd_nick(self, prefix: Optional[str], nick: Optional[str] = None):
        '''Process NICK command.'''
        if not nick:
            raise NoNicknameGivenError()
        self.req_nick = nick
        self.register_user()

    def cmd_user(self, prefix: Optional[str], username: str, hostname: str,
                 servername: str, realname: str):
        self.req_user = {'username': username, 'hostname': hostname,
                         'servername': servername, 'realname': realname}
        self.register_user()

    def register_user(self):
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
        self.server.users[self.user.nick] = self.user
        self.user.send_welcome()

    def closed(self):
        del self.server.users[self.user.nick]
