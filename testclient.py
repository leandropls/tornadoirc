# coding: utf-8

from tornado.tcpclient import TCPClient
from tornado import gen
from tornado.iostream import StreamClosedError, UnsatisfiableReadError
from tornado.ioloop import IOLoop
from random import randint

@gen.coroutine
def ircbot(nick: str, channel: str, master: str):
    stream = yield TCPClient().connect('127.0.0.1', 6667)
    stream.write(('NICK %s\r\n' % nick).encode('utf-8'))
    stream.write(b'USER bot * * :IRC Bot\r\n')
    ret = None
    while True:
        try:
            data = yield stream.read_until(b'\r\n', max_bytes = 512)
            data = data.decode('utf-8', 'ignore')
            data = data.rstrip('\r\n')
            datalist = data.split(' ')

            # Answer to PING
            if datalist[0] == 'PING':
                stream.write(('PONG %s\r\n' % datalist[1]).encode('utf-8'))
                continue

            # Join channel when motd ends
            if channel and datalist[1] == '376' or datalist[1] == '422':
                stream.write(('JOIN %s\r\n' % channel).encode('utf-8'))
                continue

            # Die on command
            if (datalist[0].split('!')[0] == (':%s' % master) and
                (datalist[1] == 'PRIVMSG' or datalist[1] == 'NOTICE') and
                datalist[3].lstrip(':') == '!die'):
                stream.write(b'QUIT :I\'m a good bot and I obey my master.\r\n')
                stream.close()
        except UnsatisfiableReadError:
            raise UnsatisfiableReadError(data)
        except StreamClosedError:
            break

@gen.coroutine
def main():
    count = 10000
    yield [ircbot(nick = 'Bot%s' % format(i, '03d'),
                  channel = None,
                  master = 'BotMaster')
           for i in range(count)]

IOLoop.instance().run_sync(main)
