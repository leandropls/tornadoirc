# coding: utf-8

from models.connection import Connection

from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.iostream import StreamClosedError

from typing import Undefined
import logging
import re

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

    def __init__(self, settings):
        self.tcpserver = IRCTCPServer(self)
        self.settings = settings
        self.name = settings['name']
        self.date = settings['date']
        self.users = {}

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
        r'\r?\n'
    )

    @gen.coroutine
    def handle_stream(self, stream, address):
        connection = Connection(stream = stream,
                                address = address[0],
                                port = address[1],
                                server = self.ircserver)
        logger.info('Connection from %s', address[0])
        while True:
            try:
                # Receive message
                try:
                    data = yield stream.read_until(b'\n', max_bytes = 512)
                except StreamClosedError:
                    connection.closed()
                    logger.info('Connection from %s closed.', address[0])
                    return
                data = data.decode('utf-8', 'ignore')

                # Parse message
                match = self.message_regex.match(data)
                if not match:
                    continue

                prefix, command, param_str = match.groups()

                if prefix:
                    prefix = prefix.split(':', maxsplit = 1)[1].rstrip()
                param_str = param_str if param_str else ''

                command = command.lower()

                params = []
                if param_str:
                    autoword = True
                    for word in param_str.split(' '):
                        if autoword or (word[0] == ':'):
                            if word[0] == ':':
                                autoword = False
                                word = word.split(':')[1] if len(word) > 1 else ''
                            params.append(word)
                        else:
                            params[-1] = '%s %s' % (params[-1], word)

                # Delgate handling of message
                connection.on_read(prefix, command, params)
            except Exception as e:
                logger.info('IOStream read loop failed: %s', str(e))
                return
