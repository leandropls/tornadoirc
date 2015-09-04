# coding: utf-8

from .util import LowerCaseDict, log_exceptions
from .exceptions import *

from typing import Undefined, Optional, Tuple, List, Dict
from datetime import datetime
from fnmatch import fnmatch
from collections import namedtuple
import logging
import re

logger = logging.getLogger('tornado.general')

ModeTuple = namedtuple('ModeTuple', ['author', 'timestamp'])
UserTuple = namedtuple('UserTuple', ['user', 'operator'])

class Channel(object):
    '''IRC channel'''
    name = Undefined(str)
    catalog = Undefined('ChannelCatalog')
    topic = Undefined(Optional[str])
    users = Undefined(LowerCaseDict) # users = {'nick': UserTuple}
    key = Undefined(Optional[str])
    banlist = Undefined(Dict[str, ModeTuple])
    invlist = Undefined(Dict[str, ModeTuple])
    exclist = Undefined(Dict[str, ModeTuple])
    _limit = Undefined(int)
    _name_regex = re.compile(r'^#\w+$')
    _knownmodes = {
         'b': {'param': True,  'method': 'mode_ban'},
         'e': {'param': True,  'method': 'mode_except'},
         'i': {'param': False, 'method': 'mode_inviteonly'},
         'k': {'param': True,  'method': 'mode_key'},
         'l': {'param': True,  'method': 'mode_limit'},
         'm': {'param': False, 'method': 'mode_moderated'},
         'I': {'param': True,  'method': 'mode_invite'},
         'o': {'param': True,  'method': 'mode_operator'},
         'O': {'param': False, 'method': 'mode_owner'},
         's': {'param': False, 'method': 'mode_secret'},
         'v': {'param': True,  'method': 'mode_voice'},
    }
    _addrmask_regex = re.compile(
        r'^((?:[\w?*]+$)|(?:[\w?*]+!))?'              # nickmask or nickmask!
        r'((?:[a-zA-Z0-9*?]+$)|(?:[a-zA-Z0-9*?]+@))?' # usermask or usermask@
        r'([a-zA-Z0-9.*?]+)?$'                        # hostmask
    )

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        chanlimit = self.catalog.server.settings['chanlimit']
        self._limit = min(chanlimit, value)

    def __init__(self, name: str, catalog: 'ChannelCatalog'):
        chanlen_max = catalog.server.settings['chanlen']
        self.set_name(value = name, chanlen_max = chanlen_max)
        self.catalog = catalog
        self.topic = None
        self.users = LowerCaseDict()
        self.key = None
        self.banlist = {}
        self.invlist = {}
        self.exclist = {}
        self._limit = catalog.server.settings['chanlimit']

    def set_name(self, value: str, chanlen_max: int):
        '''Set channel name. Raise exception if it\'s invalid.'''
        if not self._name_regex.match(value):
            raise NoSuchChannelError(channel = value)
        if len(value.encode('utf-8')) > chanlen_max:
            raise NoSuchChannelError(channel = value)
        self.name = value

    def broadcast_message(self, *args, **kwargs):
        '''Broadcast message to all channel members.'''
        for nick in self.users:
            target = self.users[nick].user
            target.send_message(*args, **kwargs)

    def join(self, user: 'User', key: Optional[str] = None):
        '''Joins user to this channel.'''
        # Check if it's already in
        if user.nick in self.users:
            return

        # Check password
        if self.key and key and self.key != key:
            raise BadChannelKeyError()

        # Check channel size limit
        if len(self.users) >= self.limit:
            raise ChannelIsFullError(channel = self.name)

        # Check ban list
        lcaddr = user.address.lower()
        for mask in self.banlist:
            if fnmatch(lcaddr, mask):
                raise BannedFromChanError(channel = self.name)

        # Join user
        operator = len(self.users) == 0
        self.users[user.nick] = UserTuple(user = user, operator = operator)
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
        if not self.users[user.nick].operator:
            raise ChanOpsPrivsNeededError(channel = self.name)
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
        nicklist = []
        for nick in users:
            if users[nick].operator:
                nicklist.append('@%s' % users[nick].user.nick)
                continue
            nicklist.append(users[nick].user.nick)
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
            target = self.users[nick].user
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
            target = self.users[nick].user
            if target.address == sender:
                continue
            target.send_notice(sender = sender, recipient = recipient,
                               text = text)

    @log_exceptions
    def send_modes(self, user: 'User'):
        '''Send channel modes to user.'''
        return

    @log_exceptions
    def mode(self, user: 'User', modes: Tuple[str]):
        '''Process MODE command for channels.'''
        if not modes:
            return
            channel.send_modes(user = self)

        knownmodes = self._knownmodes
        mlist = []
        modeiter = iter(modes)          # Eq. to "for mstr in modes", except
        while True:                     # that this way it's possible to
            try: mstr = next(modeiter)  # advance the interator from other
            except: break               # places within the loop.
            oper = '+'
            for m in mstr:
                if m == '+' or m == '-':
                    oper = m
                if m in knownmodes:
                    param = next(modeiter, '') if knownmodes[m]['param'] else ''
                    mlist.append((m, oper, param))

        operations = {}
        for m in mlist:
            operations.setdefault(m[0], []).append((m[1], m[2]))

        for m in operations:
            if hasattr(self, knownmodes[m]['method']):
                method = getattr(self, knownmodes[m]['method'])
                method(user = user, operations = operations[m])

    @log_exceptions
    def mode_invite(self, user: 'User', operations: List[Tuple[str, str]]):
        '''Process MODE +I operations'''
        self._mode_list(user = user, operations = operations, char = 'I',
                        modelist = self.exclist, listmsgid = 'RPL_INVITELIST',
                        listendmsgid = 'RPL_ENDOFINVITELIST')

    @log_exceptions
    def mode_except(self, user: 'User', operations: List[Tuple[str, str]]):
        '''Process MODE +e operations'''
        self._mode_list(user = user, operations = operations, char = 'e',
                        modelist = self.exclist, listmsgid = 'RPL_EXCEPTLIST',
                        listendmsgid = 'RPL_ENDOFEXCEPTLIST')

    @log_exceptions
    def mode_ban(self, user: 'User', operations: List[Tuple[str, str]]):
        '''Process MODE +b operations'''
        self._mode_list(user = user, operations = operations, char = 'b',
                        modelist = self.banlist, listmsgid = 'RPL_BANLIST',
                        listendmsgid = 'RPL_ENDOFBANLIST')

    @log_exceptions
    def _mode_list(self, user: 'User', operations: List[Tuple[str, str]],
                   char: str, modelist: Dict[str, Tuple[str, int]],
                   listmsgid: str, listendmsgid: str):
        '''Process MODE +b / +I / +e operations'''
        timestamp = int(datetime.now().timestamp())
        sendlist = False
        eff_modes = []
        eff_params = []
        lastoper = None
        for oper, param in operations:
            if not param: # MODE #chan +x
                sendlist = True
                continue
            if not self.users[user.nick].operator:
                raise ChanOpsPrivsNeededError(channel = self.name)

            # Parse mask
            match = self._addrmask_regex.match(param)
            if not match:
                continue
            parts = match.groups()
            logger.info(str(parts))
            if not any(parts):
                continue
            param = ('%s!' % parts[0].rstrip('!')) if parts[0] else '*!'
            param += ('%s@' % parts[1].rstrip('@')) if parts[1] else '*@'
            param += parts[2] if parts[2] else '*'
            param = param.lower()

            if oper == '+' and param not in modelist: # MODE #chan +x nick!*@*
                if oper != lastoper: eff_modes.append(oper); lastoper = oper
                eff_modes.append(char)
                eff_params.append(param)
                modelist[param] = ModeTuple(user.address, timestamp)
                continue
            if oper == '-' and param in modelist: # MODE #chan -x nick!*@*
                if oper != lastoper: eff_modes.append(oper); lastoper = oper
                eff_modes.append(char)
                eff_params.append(param)
                del modelist[param]
                continue
        if eff_modes:
            eff_str = '%s %s' % (''.join(eff_modes), ' '.join(eff_params))
            self.broadcast_message('CMD_MODE_CHAN',
                                   useraddr = user.address,
                                   channel = self.name,
                                   modes = eff_str)
        if sendlist:
            for mask in modelist:
                user.send_message(listmsgid,
                                  channel = self.name,
                                  mask = mask,
                                  author = modelist[mask].author,
                                  timestamp = modelist[mask].timestamp)
            user.send_message(listendmsgid, channel = self.name)


    @log_exceptions
    def mode_operator(self, user: 'User', operations: List[Tuple[str, str]]):
        '''Process MODE +o operations'''
        if user.nick not in self.users:
            return
        if not self.users[user.nick].operator:
            raise ChanOpsPrivsNeededError(channel = self.name)

        eff_modes = []
        eff_params = []
        lastoper = None
        for oper, param in operations:
            if param not in self.users:
                continue
            target = self.users[param]
            if oper == '+' and not target.operator: # MODE #chan +o nick
                if oper != lastoper: eff_modes.append(oper); lastoper = oper
                eff_modes.append('o')
                eff_params.append(param)
                self.users[param] = target._replace(operator = True)
                continue
            if oper == '-' and target.operator: # MODE #chan -o nick
                if oper != lastoper: eff_modes.append(oper); lastoper = oper
                eff_modes.append('o')
                eff_params.append(param)
                self.users[param] = target._replace(operator = False)
                continue
        if eff_modes:
            eff_str = '%s %s' % (''.join(eff_modes), ' '.join(eff_params))
            self.broadcast_message('CMD_MODE_CHAN',
                                   useraddr = user.address,
                                   channel = self.name,
                                   modes = eff_str)


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
