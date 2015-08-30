# coding: utf-8

from data.user import User
from data.messages import messages

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
        message = ':%(msgfrom)s ' + messages[msgid][0] + ' %(msgto)s :' + messages[msgid][1] + '\r\n'
        message = message % params
        message = message.encode('utf-8')
        self.stream.write(message)

    def on_read(self, prefix: str, command: str, params: List[str]):
        # Check if method exists
        methodname = 'cmd_%s' % command
        if not hasattr(self, methodname):
            return

        # Fetch method
        method = getattr(self, methodname)

        # Check method args
        args, _, _, defaults, _, _, _ = inspect.getfullargspec(method)
        argnum = len(args) if args else 0
        defnum = len(defaults) if defaults else 0

        # Check if we have enough parameters to call method
        if len(params) < argnum - defnum - 2:
            return # too few parameters

        # Call method
        method(prefix, *params[0:argnum - 2])

    def cmd_nick(self, prefix: Optional[str], nick: Optional[str] = None):
        if not nick:
            return # ERR_NONICKNAMEGIVEN
        self.user = User(nick = nick, connection = self, hopcount = 0)

    def cmd_user(self, prefix: Optional[str], username: str, hostname: str,
                 servername: str, realname: str):
        if not self.user:
            return

        if self.user.registered:
            return # ERR_ALREADYREGISTRED

        self.user.register(username = '~' + username,
                           hostname = self.address,
                           servername = 'not-implemented',
                           realname = realname)
