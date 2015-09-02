# coding: utf-8

from .exceptions import CommandError

from inspect import signature
import functools, sys, os
import logging

logger = logging.getLogger('tornado.general')

def log_exceptions(f):
    '''Catch exception in method, format message and log it.'''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CommandError:
            raise
        except Exception as e:
            error_type = sys.exc_info()[0].__name__
            error_desc = str(e)
            error_file = os.path.basename(sys.exc_info()[2].tb_next.tb_frame.f_code.co_filename)
            error_line = sys.exc_info()[2].tb_next.tb_lineno
            logger.info('Exception at %s (line: %s), %s: %s',
                        error_file, error_line, error_type, error_desc)
            return

    wrapper.__signature__ = signature(f)
    return wrapper

class LowerCaseDict(dict):
    '''Dict compatible class that convert str keys to lower case keys.'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self:
            lc = key.lower()
            if key != lc:
                super().__setitem__(lc, super().__getitem__(key))
                super().__delitem__(key)

    def __contains__(self, key, *args, **kwargs):
        return super().__contains__(key.lower(), *args, **kwargs)

    def __delitem__(self, key, *args, **kwargs):
        return super().__delitem__(key.lower(), *args, **kwargs)

    def __getitem__(self, key, *args, **kwargs):
        return super().__getitem__(key.lower(), *args, **kwargs)

    def __setitem__(self, key, *args, **kwargs):
        super().__setitem__(key.lower(), *args, **kwargs)

    def fromkeys(self, iterable, *args, **kwargs):
        iterable = (x.lower() for x in iterable)
        return super().fromkeys(iterable, *args, **kwargs)

    def get(self, k, *args, **kwargs):
        return super().get(k.lower(), *args, **kwargs)

    def pop(self, k, *args, **kwargs):
        return super().pop(k.lower(), *args, **kwargs)

    def setdefault(self, k, *args, **kwargs):
        return super().setdefault(k.lower(), *args, **kwargs)

    def update(self, E = None, **F):
        if E:
            if hasattr(E, 'keys'):
                for k in E:
                    self[k] = E[k]
            else:
                for k, v in E:
                    self[k] = v
        for k in F:
            self[k] = F[k]
