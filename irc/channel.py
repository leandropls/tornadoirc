# coding: utf-8

from .util import LowerCaseDict
from .exceptions import *

from typing import Undefined, Optional
import logging

logger = logging.getLogger('tornado.general')

class Channel(object):
    '''IRC channel'''
    name = Undefined(str)
    topic = Undefined(Optional[str])
    users = Undefined(LowerCaseDict) # users = {'nick': {'user': user}}

    def __init__(self, name: str, catalog: 'ChannelCatalog'):
        if not name or name[0] != '#':
            raise NoSuchChannelError(channel = name)

        self.name = name
        self.topic = None
        self.users = LowerCaseDict()

    def broadcast_message(self, *args, **kwargs):
        '''Broadcast message to all channel members.'''
        for nick in self.users:
            target = self.users[nick]['user']
            target.send_message(*args, **kwargs)

    def join(self, user: 'User'):
        '''Joins user to this channel.'''
        self.users[user.nick] = {'user': user}
        self.broadcast_message('CMD_JOIN',
                               useraddr = user.address,
                               channel = self.name)
        self.send_topic(user)
        self.send_names(user)

    def part(self, user: 'User', message: str = ''):
        '''Parts user from this channel.'''
        if user.nick not in users:
            raise NotOnChannelError()
        self.broadcast_message('CMD_PART',
                               useraddr = user.address,
                               channel = self.name,
                               message = message)
        del users[user.nick]

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

    def send_names(self, user: 'User'):
        '''Send current channel members nicks to user.'''
        users = self.users
        nicklist = [users[nick]['user'].nick for nick in users]
        nicklist = ' '.join(nicklist)
        user.send_message('RPL_NAMREPLY',
                          channel = self.name,
                          chantype = '=',
                          nicklist = nicklist)
        user.send_message('RPL_ENDOFNAMES', channel = self.name)

class ChannelCatalog(LowerCaseDict):
    '''Catalog with all channels within an IRC server/network.'''

    def join(self, user: 'User', name: str):
        '''Add an user to a channel. Returns channel.'''
        if name in self:
            channel = self[name]
        else:
            channel = Channel(name = name, catalog = self)
            self[name] = channel
        channel.join(user)
        return channel
