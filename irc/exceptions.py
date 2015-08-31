# coding: utf-8

from .messages import messages

from typing import Undefined

class CommandError(Exception):
    msgid = Undefined(str)
    msgparams = Undefined(dict)

##
# Errors with messages 431 ~ 436
##
class NoNicknameGivenError(CommandError):
    '''431 - No nickname given'''
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NONICKNAMEGIVEN'
        self.msgparams = {}

class ErroneousNicknameError(CommandError):
    '''432 - Erroneous nickname'''
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_ERRONEUSNICKNAME'
        self.msgparams = {'nick': nick}

class NicknameInUseError(CommandError):
    '''433 - Nickname is already in use'''
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NICKNAMEINUSE'
        self.msgparams = {'nick': nick}

class NickCollisionError(CommandError):
    '''436 - Nickname collision'''
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NICKCOLLISION'
        self.msgparams = {'nick': nick}

##
# Other
##
class NoSuchNickError(CommandError):
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NOSUCHNICK'
        self.msgparams = {'nick': nick}

class NoSuchServerError(CommandError):
    '''402 - No such server'''
    def __init__(self, servername: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NOSUCHSERVER'
        self.msgparams = {'servername': servername}

class NoMotdError(CommandError):
    '''422 - You may not reregister'''
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NOMOTD'
        self.msgparams = {}

class NeedMoreParamsError(CommandError):
    '''461 - Not enough parameters'''
    def __init__(self, command: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_NEEDMOREPARAMS'
        self.msgparams = {'command': command}

class AlreadyRegisteredError(CommandError):
    '''462 - You may not reregister'''
    def __init__(self, nick: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.msgid = 'ERR_ALREADYREGISTRED'
        self.msgparams = {}
