# coding: utf-8

from .exceptions import *
from .util import LowerCaseDict

from tornado.ioloop import IOLoop

from typing import Undefined, Optional, List, Tuple
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
    server = Undefined('IRCServer')
    channels = Undefined(LowerCaseDict)
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

        if value.lower() == self._nick.lower():
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
    def __init__(self, nick: str, connection: 'Connection', server: 'Server',
                 hopcount: int, username: str, hostname: str, servername: str,
                 realname: str):
        self.connection = connection
        self.server = server
        self._nick = ''
        self.nick = nick
        self.hopcount = hopcount
        self.username = username
        self.hostname = hostname
        self.servername = servername
        self.realname = realname
        self.channels = LowerCaseDict()

        logger.info('Registered new user: %s!%s@%s',
                    self.nick, self.username, self.hostname)

    ##
    # Events
    ##
    def on_register(self):
        self.send_welcome()

    def on_close(self):
        io_loop = IOLoop.current()
        if self.pingtimer:
            io_loop.remove_timeout(self.pingtimer)
            self.pingtimer = None
        if self.timeouttimer:
            io_loop.remove_timeout(self.timeouttimer)
            self.timeoutttimer = None
        del self.server.users[self.nick]

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

        self.cmd_lusers()
        self.cmd_motd()
        self.send_ping()

    def send_privmsg(self, sender: str, recipient: str, text: str):
        '''Send PRIVMSG command to user.'''
        self.send_message('CMD_PRIVMSG',
                          sender = sender,
                          recipient = recipient,
                          text = text)

    def send_notice(self, sender: str, recipient: str, text: str):
        '''Send NOTICE command to user.'''
        self.send_message('CMD_NOTICE',
                          sender = sender,
                          recipient = recipient,
                          text = text)

    ##
    # Server command handlers
    ##
    def cmd_ping(self, payload: str, destination: Optional[str] = None):
        '''Process PING command.'''
        if destination and destination != self.server.name:
            raise NoSuchServerError(servername = destination)
        self.send_message('CMD_PONG', payload = payload)

    def cmd_pong(self, payload: str):
        IOLoop.current().remove_timeout(self.timeouttimer)
        self.timeouttimer = None

    def cmd_nick(self, nick: str):
        '''Process NICK command.'''
        oldaddr = self.address
        oldnick = self.nick
        self.nick = nick
        if self.nick.lower() != oldnick.lower():
            self.server.users[self.nick] = self
            del self.server.users[oldnick]

        self.send_message('CMD_NICK', oldaddr = oldaddr, nick = self.nick)

    def cmd_privmsg(self, target: str, text: str):
        '''Process PRIVMSG command.'''
        if target not in self.server.router:
            raise NoSuchNickError(nick = target)
        entity = self.server.router[target]
        entity.send_privmsg(sender = self.address,
                            recipient = target,
                            text = text)

    def cmd_notice(self, target: str, text: str):
        '''Process NOTICE command.'''
        if target not in self.server.router:
            return
        entity = self.server.router[target]
        entity.send_privmsg(sender = self.address,
                            recipient = target,
                            text = text)

    def cmd_profiling(self):
        '''Process PROFILING command.'''
        import yappi
        stats = yappi.get_func_stats()
        self.send_notice(origin = self.server.name,
                          text = 'name\tncall\ttsub\ttot\ttavg')
        for row in stats:
            self.send_notice(origin = self.server.name,
                text = '%s\t%s\t%s\t%s\t%s' % (row[12][-44:-1],
                                               format(row[4] / row[3], '.5f'),
                                               format(row[7], '.5f'),
                                               format(row[6], '.5f'),
                                               format(row[11], '.5f')))
    def cmd_quit(self, message: str = ''):
        '''Process QUIT command.'''
        self.send_message('CMD_ERROR', text = 'Quit: %s' % message)
        self.connection.stream.close()

    ##
    # RFC2812 - 3.2 Channel operations
    ##
    def cmd_join(self, channel: str, *chanlist: Tuple[str]):
        '''Process JOIN Command.'''
        chanlist = list(chanlist)
        chanlist.insert(0, channel)
        chancatalog = self.server.channels
        for name in chanlist:
            if not name:
                continue
            chancatalog.join(user = self, name = name.split(',')[0])

    def cmd_part(self, channel: str, *params: Tuple[str]):
        '''Process PART command.'''
        params = list(params)
        params.insert(0, channel)

        # Separate message and channels
        message = None
        chanlist = []
        addmessage = False
        for par in params:
            logger.info(par)
            if not par:
                continue
            if par[-1] == ',':
                addmessage = True
            if not addmessage:
                chanlist.append(par)
            else:
                message = par
                break

        # Part channels
        for name in chanlist:
            if name not in self.channels:
                raise NotOnChannelError(channel = name)
            channel = self.channels[name]
            channel.part(self, message)

    ##
    # RFC2812 - 3.4 Server queries and commands
    ##
    def cmd_motd(self, target: Optional[str] = None):
        '''Process MOTD command.'''
        if not self.server.settings['motd']:
            raise NoMotdError()
        self.send_message('RPL_MOTDSTART')
        for text in self.server.settings['motd']:
            self.send_message('RPL_MOTD', text = text[0 : min(len(text) + 1, 81)])
        self.send_message('RPL_ENDOFMOTD')

    def cmd_lusers(self, mask: Optional[str] = None,
                   target: Optional[str] = None):
        '''Process LUSERS command.'''
        self.send_message('RPL_LUSERCLIENT',
                          usercount = len(self.server.users),
                          servicescount = 0,
                          serverscount = 1)
        self.send_message('RPL_LUSERME',
                          usercount = len(self.server.users),
                          serverscount = 0)

    ##
    # RFC2812 - 3.6 User based queries
    ##
    def cmd_whois(self, par1: str, par2: Optional[str] = None):
        '''Process WHOIS command.'''
        if par2:
            target = par1
            mask = par2
        else:
            target = None
            mask = par1
        nick = mask.split('!')[0]

        if nick not in self.server.users:
            raise NoSuchNickError(nick = nick)
        user = self.server.users[nick]

        self.send_message('RPL_WHOISUSER', nick = user.nick,
                          username = user.username, hostname = user.hostname,
                          realname = user.realname)
        self.send_message('RPL_WHOISSERVER', nick = user.nick,
                          servername = user.servername,
                          serverinfo = '')
        self.send_message('RPL_ENDOFWHOIS', nick = user.nick)

    ##
    # RFC2812 - 4. Optional features
    ##
    def cmd_ison(self, nick: str, *nicklist: List[str]):
        '''Process ISON command.'''
        nicklist = list(nicklist)
        nicklist.insert(0, nick)
        users = self.server.users
        online = [nick for nick in nicklist if nick in users]
        online = ' '.join(online)
        self.send_message('RPL_ISON', nicklist = online)
