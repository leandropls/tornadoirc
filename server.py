#!/usr/bin/env python3
# coding: utf-8

import settings
from settings import ircd as ircdsettings
from irc.server import IRCServer

from setproctitle import setproctitle # pylint: disable=no-name-in-module
from tornado.options import define, options
from tornado.ioloop import IOLoop
from tornado import autoreload

def main() -> None:
    '''Runs server'''

    # Parse options
    define('production',
               default = False,
               help = 'run in production mode',
               type = bool)
    options.parse_command_line()

    # Set server name
    pname = settings.process_name if settings.process_name else None
    if pname:
        setproctitle(pname)

    # Register IRC server
    server = IRCServer(settings = ircdsettings)
    for address, port in ircdsettings['listen']:
        server.listen(port, address = address)

    # Start profiling
    if settings.profiling:
        import yappi
        yappi.start()

    # Setup autoreload
    autoreload.start()

    # Run application
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
