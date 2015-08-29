# coding: utf-8

from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.iostream import StreamClosedError

import logging
import re

logger = logging.getLogger('tornado.general')

class IrcServer(TCPServer):
    regex = {
        'message': re.compile( # fixme: needs improvement
            r'(?P<prefix>:\w+ +)?'
            r'(?P<command>[a-zA-Z]+|[0-9]{3})'
            r'(?P<params>[ ]+:[\w ]+)\r?\n'
        )
    }

    @gen.coroutine
    def handle_stream(self, stream, address):
        logger.info('Connection from %s', address[0])
        while True:
            try:
                try:
                    data = yield stream.read_until(b'\n', max_bytes = 512)
                except StreamClosedError:
                    return
                data = data.decode('utf-8', 'ignore')

                match = self.regex['message'].match(data)
                if not match:
                    continue

                prefix, command, params = match.groups()

                if prefix:
                    prefix = prefix.split(':', maxsplit = 1)[1].rstrip()
                params = params.split(':', maxsplit = 1)[1].rstrip()
                
                logger.info('%s, %s, %s', prefix, command, params)
            except:
                return
