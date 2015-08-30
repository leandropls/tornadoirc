# coding: utf-8

from models.user import User
from models.messages import messages

from tornado.iostream import IOStream

from typing import Undefined, List, Optional
import logging
import inspect

logger = logging.getLogger('tornado.general')

class Connection(object):
    stream = Undefined(IOStream)
    address = Undefined(str)
    port = Undefined(int)
    server = Undefined('server')
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

    def send_message(self, msgid: str, **params):
        message = ':%(msgfrom)s ' + messages[msgid][0] + ' %(msgto)s ' + messages[msgid][1] + '\r\n'
        message = message % params
        message = message.encode('utf-8')
        self.stream.write(message)

    def on_read(self, prefix: str, command: str, params: List[str]):
        # Created method name
        methodname = 'cmd_%s' % command

        # Check if method exists and fetch it if it does
        if self.user and self.user.registered:
            if not hasattr(self.user, methodname):
                return
            method = getattr(self.user, methodname)
        else:
            if not hasattr(self, methodname):
                return
            method = getattr(self, methodname)

        # Check method args
        args, _, _, defaults, _, _, _ = inspect.getfullargspec(method)
        argnum = len(args) if args else 0
        defnum = len(defaults) if defaults else 0

        # Check if we have enough parameters to call method
        if len(params) < argnum - defnum - 2:
            self.send_message('ERR_NEEDMOREPARAMS',
                              msgfrom = self.server.name,
                              msgto = self.user.nick if self.user else '',
                              command = command)
            return

        # Call method
        method(prefix, *params[0:argnum - 2])

    def cmd_nick(self, prefix: Optional[str], nick: Optional[str] = None):
        if not nick:
            self.send_message('ERR_NONICKNAMEGIVEN',
                              msgfrom = self.server.name,
                              msgto = '')
            return
        self.user = User(nick = nick, server = self.server,
                         connection = self, hopcount = 0)

    def cmd_user(self, prefix: Optional[str], username: str, hostname: str,
                 servername: str, realname: str):
        if not self.user:
            return

        if self.user.registered:
            self.send_message('ERR_ALREADYREGISTRED',
                              msgfrom = self.server.name,
                              msgto = self.user.nick)
            return

        self.user.register(username = '~' + username,
                           hostname = self.address,
                           servername = 'not-implemented',
                           realname = realname)
