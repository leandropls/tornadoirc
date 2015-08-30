# coding: utf-8

messages = {
    'RPL_WELCOME':          ('001', ':Welcome to the Internet Relay Network %(nick)s!%(username)s@%(hostname)s'),
    'RPL_YOURHOST':         ('002', ':Your host is %(servername)s, running version %(version)s'),
    'RPL_CREATED':          ('003', ':This server was created %(date)s'),
    'RPL_MYINFO':           ('004', ':%(servername)s %(version)s %(usermodes)s %(channelmodes)s'),
    'RPL_MOTD':             ('372', ':- %(text)s'),
    'RPL_MOTDSTART':        ('375', ':- %(servername)s Message of the day - '),
    'RPL_ENDOFMOTD':        ('376', ':End of MOTD command'),
    'ERR_NOMOTD':           ('422', ':MOTD File is missing'),
    'ERR_NONICKNAMEGIVEN':  ('431', ':No nickname given'),
    'ERR_ERRONEUSNICKNAME': ('432', '%(nick)s :Erroneus nickname'),
    'ERR_NICKNAMEINUSE':    ('433', '%(nick)s :Nickname is already in use'),
    'ERR_NICKCOLLISION':    ('436', '%(nick)s :Nickname collision KILL'),
    'ERR_NEEDMOREPARAMS':   ('461', '%(command)s :Not enough parameters'),
    'ERR_ALREADYREGISTRED': ('462', ':You may not reregister'),
}
