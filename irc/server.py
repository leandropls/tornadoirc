# coding: utf-8

from .connection import Connection
from .util import LowerCaseDict
from .channel import ChannelCatalog
from .router import EntityRouter

from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.iostream import StreamClosedError

from typing import Undefined
import logging
import re
import sys
import os.path

logger = logging.getLogger('tornado.general')

__all__ = ['IRCServer']

class IRCServer(object):
    tcpserver = Undefined('IRCTCPServer')
    name = Undefined(str)
    date = Undefined(str)
    version = 'tornadoirc-0.0'
    usermodes = ''
    channelmodes = ''
    users = Undefined(dict)
    channels = Undefined(ChannelCatalog)
    router = Undefined(EntityRouter)

    def __init__(self, settings):
        self.tcpserver = IRCTCPServer(self)
        self.settings = settings
        self.name = settings['name']
        self.date = settings['date']
        self.users = LowerCaseDict()
        self.channels = ChannelCatalog()
        self.router = EntityRouter(('',  self.users),
                                   ('#', self.channels))

    def listen(self, *args, **kwargs):
        '''Listen to address and port.'''
        self.tcpserver.listen(*args, **kwargs)

class IRCTCPServer(TCPServer):
    ircserver = None

    def __init__(self, ircserver, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ircserver = ircserver

    message_regex = re.compile(
        r'(?P<prefix>:\S+)?'
        r'[ ]*'
        r'(?P<command>[a-zA-Z]+|[0-9]{3})'
        r'[ ]*'
        r'(?P<params>[\S: ]+)?'
    )

    @gen.coroutine
    def handle_stream(self, stream, address):
        connection = Connection(stream = stream,
                                address = address[0],
                                port = address[1],
                                server = self.ircserver)
        logger.info('Connection from %s', address[0])
        while True:
            # Receive message
            try:
                data = yield stream.read_until(b'\n', max_bytes = 512)
                data = data.decode('utf-8', 'ignore')
                data = data.rstrip('\r\n')

                # Parse message
                match = self.message_regex.match(data)
                if not match:
                    continue

                prefix, command, param_str = match.groups()

                if prefix:
                    prefix = prefix.split(':', maxsplit = 1)[1].rstrip()
                param_str = param_str if param_str else ''

                params = []
                autoword = True
                for word in param_str.split(' '):
                    if not word:
                        continue
                    if autoword or (word[0] == ':'):
                        if word[0] == ':':
                            autoword = False
                            word = word.split(':')[1] if len(word) > 1 else ''
                        params.append(word)
                    else:
                        params[-1] = '%s %s' % (params[-1], word)

                # Delgate handling of message
                connection.on_read(prefix, command, params)
            except StreamClosedError:
                connection.on_close()
                logger.info('Connection from %s closed.', address[0])
                return
            except Exception as e:
                error_desc = '(%s) %s' % (sys.exc_info()[0].__name__, str(e))
                error_file = os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename)
                error_line = sys.exc_info()[2].tb_lineno
                logger.info('IOStream read loop failed at %s (line: %s): %s',
                            error_file, error_line, error_desc)
                return
