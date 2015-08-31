# coding: utf-8

from typing import Undefined

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
    def __init__(self, servername: str):
        super().__init__()
        self.msgid = 'ERR_NOSUCHSERVER'
        self.msgparams = {'servername': servername}

class NoSuchChannelError(CommandError):
    '''403 - No such channel'''
    def __init__(self, channel: str):
        super().__init__()
        self.msgid = 'ERR_NOSUCHCHANNEL'
        self.msgparams = {'channel': channel}

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
