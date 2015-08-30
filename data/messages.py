# coding: utf-8

messages = {
    'RPL_WELCOME':
        ('001', ':Welcome to the Internet Relay Network '
                '%(nick)s!%(username)s@%(hostname)s'),
    'RPL_YOURHOST':
        ('002', ':Your host is %(servername)s, running version %(version)s'),
    'RPL_CREATED':
        ('003', ':This server was created %(date)s'),
    'RPL_MYINFO':
        ('004', ':%(servername)s %(version)s %(usermodes)s %(channelmodes)s'),
    'ERR_NONICKNAMEGIVEN':
        ('431', ':No nickname given'),
    'ERR_NEEDMOREPARAMS':
        ('461', '%(command)s :Not enough parameters'),
    'ERR_ALREADYREGISTRED':
        ('462', ':You may not reregister'),
}
