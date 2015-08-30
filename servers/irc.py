# coding: utf-8

from data.connection import Connection
from data.server import Server

from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.iostream import StreamClosedError

from typing import Undefined
import logging
import re

logger = logging.getLogger('tornado.general')

class IrcServer(TCPServer):
    ircserver = Undefined(Server)

    def __init__(self, servername, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ircserver = Server(servername)

    regex = {
        'message': re.compile(
            r'(?P<prefix>:\S+)?'
            r'[ ]*'
            r'(?P<command>[a-zA-Z]+|[0-9]{3})'
            r'[ ]*'
            r'(?P<params>[\S: ]+)'
            r'\r?\n'
        )
    }

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
                    logger.info('Connection from %s closed.', address[0])
                    return
                data = data.decode('utf-8', 'ignore')

                # Parse message
                match = self.regex['message'].match(data)
                if not match:
                    continue

                prefix, command, param_str = match.groups()

                if prefix:
                    prefix = prefix.split(':', maxsplit = 1)[1].rstrip()

                command = command.lower()

                params = []
                autoword = True
                for word in param_str.split(' '):
                    if autoword or word[0] == ':':
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
