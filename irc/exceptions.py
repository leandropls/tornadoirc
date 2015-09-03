# coding: utf-8

from typing import Undefined

class TooLongMessageException(Exception):
    length = None
    def __init__(self, length):
        self.length = length

class CommandError(Exception):
    msgid = Undefined(str)
    msgparams = Undefined(dict)

##
# Errors with messages 431 ~ 436
##
class NoNicknameGivenError(CommandError):
    '''431 - No nickname given'''
    def __init__(self):
        super().__init__()
        self.msgid = 'ERR_NONICKNAMEGIVEN'
        self.msgparams = {}

class ErroneousNicknameError(CommandError):
    '''432 - Erroneous nickname'''
    def __init__(self, nick: str):
        super().__init__()
        self.msgid = 'ERR_ERRONEUSNICKNAME'
        self.msgparams = {'nick': nick}

class NicknameInUseError(CommandError):
    '''433 - Nickname is already in use'''
    def __init__(self, nick: str):
        super().__init__()
        self.msgid = 'ERR_NICKNAMEINUSE'
        self.msgparams = {'nick': nick}

class NickCollisionError(CommandError):
    '''436 - Nickname collision'''
    def __init__(self, nick: str):
        super().__init__()
        self.msgid = 'ERR_NICKCOLLISION'
        self.msgparams = {'nick': nick}

##
# Other
##
class NoSuchNickError(CommandError):
    '''401 - No such nick'''
    def __init__(self, nick: str):
        super().__init__()
        self.msgid = 'ERR_NOSUCHNICK'
        self.msgparams = {'nick': nick}

class NoSuchServerError(CommandError):
    '''402 - No such server'''
    def __init__(self, server: str):
        super().__init__()
        self.msgid = 'ERR_NOSUCHSERVER'
        self.msgparams = {'server': server}

class NoSuchChannelError(CommandError):
    '''403 - No such channel'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_NOSUCHCHANNEL'
        self.msgparams = {'channel': channel}

class CannotSendToChanError(CommandError):
    '''404 - Cannot send to channel'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_CANNOTSENDTOCHAN'
        self.msgparams = {'channel': channel}

class UnknownCommandError(CommandError):
    '''421 - Unknown command'''
    def __init__(self, command):
        super().__init__()
        self.msgid = 'ERR_UNKNOWNCOMMAND'
        self.msgparams = {'command': command}

class NoMotdError(CommandError):
    '''422 - You may not reregister'''
    def __init__(self):
        super().__init__()
        self.msgid = 'ERR_NOMOTD'
        self.msgparams = {}

class NotOnChannelError(CommandError):
    '''442 - No such channel'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_NOTONCHANNEL'
        self.msgparams = {'channel': channel}

class NeedMoreParamsError(CommandError):
    '''461 - Not enough parameters'''
    def __init__(self, command: str):
        super().__init__()
        self.msgid = 'ERR_NEEDMOREPARAMS'
        self.msgparams = {'command': command}

class AlreadyRegisteredError(CommandError):
    '''462 - You may not reregister'''
    def __init__(self):
        super().__init__()
        self.msgid = 'ERR_ALREADYREGISTRED'
        self.msgparams = {}

class ChannelIsFullError(CommandError):
    '''471 - Cannot join channel (+l)'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_CHANNELISFULL'
        self.msgparams = {'channel': channel}

class BannedFromChanError(CommandError):
    '''474 - Cannot join channel (+b)'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_BANNEDFROMCHAN'
        self.msgparams = {'channel': channel}

class BadChannelKeyError(CommandError):
    '''475 - Cannot join channel (+k)'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_BADCHANNELKEY'
        self.msgparams = {'channel': channel}
