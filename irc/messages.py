# coding: utf-8

#    311    RPL_WHOISUSER
#               "<nick> <user> <host> * :<real name>"
#        312    RPL_WHOISSERVER
#               "<nick> <server> :<server info>"
#        313    RPL_WHOISOPERATOR
#               "<nick> :is an IRC operator"
#
#
#
#
# Kalt                         Informational                     [Page 44]
#
# RFC 2812          Internet Relay Chat: Client Protocol        April 2000
#
#
#        317    RPL_WHOISIDLE
#               "<nick> <integer> :seconds idle"
#        318    RPL_ENDOFWHOIS
#               "<nick> :End of WHOIS list"
#        319    RPL_WHOISCHANNELS
#               "<nick> :*( ( "@" / "+" ) <channel> " " )"

messages = {
    'RPL_WELCOME':          ':%(servername)s 001 %(target)s :Welcome to the Internet Relay Network %(targetaddr)s',
    'RPL_YOURHOST':         ':%(servername)s 002 %(target)s :Your host is %(servername)s, running version %(version)s',
    'RPL_CREATED':          ':%(servername)s 003 %(target)s :This server was created %(date)s',
    'RPL_MYINFO':           ':%(servername)s 004 %(target)s :%(servername)s %(version)s %(usermodes)s %(channelmodes)s',
    'RPL_LUSERCLIENT':      ':%(servername)s 251 %(target)s :There are %(usercount)s users and %(servicescount)s services on %(serverscount)s servers',
    'RPL_LUSERME':          ':%(servername)s 255 %(target)s :I have %(usercount)s clients and %(serverscount)s servers',
    'RPL_ISON':             ':%(servername)s 303 %(target)s :%(nicklist)s',
    'RPL_WHOISUSER':        ':%(servername)s 311 %(target)s %(nick)s %(username)s %(hostname)s * :%(realname)s',
    'RPL_WHOISSERVER':      ':%(servername)s 312 %(target)s %(nick)s %(servername)s :%(serverinfo)s',
    'RPL_ENDOFWHOIS':       ':%(servername)s 318 %(target)s %(nick)s :End of WHOIS list',
    'RPL_NOTOPIC':          ':%(servername)s 331 %(target)s %(channel)s :No topic is set',
    'RPL_TOPIC':            ':%(servername)s 332 %(target)s %(channel)s :%(topic)s',
    'RPL_NAMREPLY':         ':%(servername)s 353 %(target)s %(chantype)s %(channel)s :%(nicklist)s',
    'RPL_ENDOFNAMES':       ':%(servername)s 366 %(target)s %(channel)s :End of NAMES list',
    'RPL_MOTD':             ':%(servername)s 372 %(target)s :- %(text)s',
    'RPL_MOTDSTART':        ':%(servername)s 375 %(target)s :- %(servername)s Message of the day - ',
    'RPL_ENDOFMOTD':        ':%(servername)s 376 %(target)s :End of MOTD command',

    'ERR_NOSUCHNICK':       ':%(servername)s 401 %(target)s %(nick)s :No such nick/channel',
    'ERR_NOSUCHSERVER':     ':%(servername)s 402 %(target)s %(servername)s :No such server',
    'ERR_NOSUCHCHANNEL':    ':%(servername)s 403 %(target)s %(channel)s :No such channel',
    'ERR_NOMOTD':           ':%(servername)s 422 %(target)s :MOTD File is missing',
    'ERR_NONICKNAMEGIVEN':  ':%(servername)s 431 %(target)s :No nickname given',
    'ERR_ERRONEUSNICKNAME': ':%(servername)s 432 %(target)s %(nick)s :Erroneus nickname',
    'ERR_NICKNAMEINUSE':    ':%(servername)s 433 %(target)s %(nick)s :Nickname is already in use',
    'ERR_NICKCOLLISION':    ':%(servername)s 436 %(target)s %(nick)s :Nickname collision KILL',
    'ERR_NOTONCHANNEL':     ':%(servername)s 442 %(target)s %(channel)s :You\'re not on that channel',
    'ERR_NEEDMOREPARAMS':   ':%(servername)s 461 %(target)s %(command)s :Not enough parameters',
    'ERR_ALREADYREGISTRED': ':%(servername)s 462 %(target)s :You may not reregister',

    'CMD_ERROR':            'ERROR :Closing Link: %(ipaddr)s (%(text)s)',
    'CMD_NICK':             ':%(oldaddr)s NICK :%(nick)s',
    'CMD_PING':             'PING :%(servername)s',
    'CMD_PONG':             ':%(servername)s PONG %(servername)s :%(payload)s',
    'CMD_PRIVMSG':          ':%(originaddr)s PRIVMSG %(target)s :%(text)s',
    'CMD_NOTICE':           ':%(originaddr)s NOTICE %(target)s :%(text)s',
    'CMD_JOIN':             ':%(useraddr)s JOIN %(channel)s',
    'CMD_PART':             ':%(useraddr)s PART %(channel)s :%(message)s',
    'CMD_TOPIC':            ':%(useraddr)s TOPIC %(channel)s :%(topic)s',
}
