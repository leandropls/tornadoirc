# coding: utf-8

from .util import LowerCaseDict, log_exceptions
from .exceptions import *

from typing import Undefined, Optional
import logging

logger = logging.getLogger('tornado.general')

class Channel(object):
    '''IRC channel'''
    _name = Undefined(str)
    catalog = Undefined('ChannelCatalog')
    topic = Undefined(Optional[str])
    users = Undefined(LowerCaseDict) # users = {'nick': {'user': user}}
    key = Undefined(Optional[str])
    _limit = Undefined(int)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        chanlimit = self.catalog.server.settings['chanlimit']
        self._limit = min(chanlimit, value)

    def __init__(self, name: str, catalog: 'ChannelCatalog'):
        if not name or name[0] != '#':
            raise NoSuchChannelError(channel = name)

        self.name = name
        self.catalog = catalog
        self.topic = None
        self.users = LowerCaseDict()
        self.key = None
        self._limit = catalog.server.settings['chanlimit']

    def broadcast_message(self, *args, **kwargs):
        '''Broadcast message to all channel members.'''
        for nick in self.users:
            target = self.users[nick]['user']
            target.send_message(*args, **kwargs)

    def join(self, user: 'User', key: Optional[str] = None):
        '''Joins user to this channel.'''
        if user.nick in self.users:
            return
        if self.key and key and self.key != key:
            raise BadChannelKeyError()
        if len(self.users) >= self.limit:
            raise ChannelIsFullError(channel = self.name)

        self.users[user.nick] = {'user': user}
        user.channels[self.name] = self
        self.broadcast_message('CMD_JOIN',
                               useraddr = user.address,
                               channel = self.name)
        self.send_topic(user)
        self.send_names(user)

    def part(self, user: 'User', message: str = None):
        '''Parts user from this channel.'''
        if user.nick not in self.users:
            raise NotOnChannelError()
        if not message:
            message = ''
        self.broadcast_message('CMD_PART',
                               useraddr = user.address,
                               channel = self.name,
                               message = message)
        del self.users[user.nick]
        del user.channels[self.name]

        if len(self.users) == 0:
            catalog = self.catalog
            self.catalog = None
            del catalog[self.name]
            self.server = None

    def quit(self, user: 'User', message: str = None):
        '''Parts user from this channel.'''
        if not message:
            message = ''
        self.broadcast_message('CMD_QUIT',
                               useraddr = user.address,
                               message = message)
        if user.nick in self.users:
            del self.users[user.nick]
        if self.name in user.channels:
            del user.channels[self.name]

    def set_topic(self, user: 'User', topic: str = ''):
        '''Sets channel topic.'''
        self.topic = topic
        self.broadcast_message('CMD_TOPIC',
                               useraddr = user.address,
                               channel = self.name,
                               topic = topic)

    def send_topic(self, user: 'User'):
        '''Send channel topic to user.'''
        if self.topic:
            user.send_message('RPL_TOPIC',
                              channel = self.name, topic = self.topic)
        else:
            user.send_message('RPL_NOTOPIC', channel = self.name)

    @log_exceptions
    def send_names(self, user: 'User', suppress_end = False):
        '''Send current channel members nicks to user.'''
        users = self.users
        nicklist = [users[nick]['user'].nick for nick in users]
        nicklist_str = ' '.join(nicklist)
        try:
            user.send_message('RPL_NAMREPLY',
                              channel = self.name,
                              chantype = '=',
                              nicklist = nicklist_str)
        except TooLongMessageException as e:
            length = e.length
            baselen = length - len(nicklist_str.encode('utf-8'))
            maxnicks = (512 - baselen) // user.server.settings['nicklen']
            if maxnicks <= 0:
                raise
            for i in range(0, len(nicklist) // maxnicks + 1):
                nicklist_str = ' '.join(nicklist[maxnicks * i:maxnicks * i + maxnicks])
                user.send_message('RPL_NAMREPLY',
                                  channel = self.name,
                                  chantype = '=',
                                  nicklist = nicklist_str)
                start = maxnicks

        if not suppress_end:
            user.send_message('RPL_ENDOFNAMES', channel = self.name)

    def send_privmsg(self, sender: str, recipient: str, text: str):
        '''Send PRIVMSG command to channel\'s users.'''
        sendernick = sender.split('!')[0]
        if sendernick not in self.users:
            raise CannotSendToChanError()

        for nick in self.users:
            target = self.users[nick]['user']
            if target.address == sender:
                continue
            target.send_privmsg(sender = sender, recipient = recipient,
                                text = text)

    def send_notice(self, sender: str, recipient: str, text: str):
        '''Send NOTICE command to channel\'s users.'''
        sendernick = sender.split('!')[0]
        if sendernick not in self.users:
            return

        for nick in self.users:
            target = self.users[nick]['user']
            if target.address == sender:
                continue
            target.send_notice(sender = sender, recipient = recipient,
                               text = text)


class ChannelCatalog(LowerCaseDict):
    '''Catalog with all channels within an IRC server/network.'''
    server = Undefined('Server')

    def __init__(self, server: 'Server', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server

    def join(self, user: 'User', name: str, key: Optional[str] = None):
        '''Add an user to a channel. Returns channel.'''
        # Create or get channel
        if name in self:
            channel = self[name]
        else:
            channel = Channel(name = name, catalog = self)
            self[name] = channel

        # Join
        if key:
            channel.join(user = user, key = key)
        else:
            channel.join(user = user)
