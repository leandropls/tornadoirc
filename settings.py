# coding: utf-8

##
# Process
##
process_name = 'tornadoircd'

##
# Local time
##
import pytz, datetime
localtime = pytz.timezone('America/Sao_Paulo')
now = datetime.datetime.now(localtime)

##
# IRCd
##
from datetime import datetime
ircd = {
    'name': 'irc.testnetwork.org',
    'date': str(now),
    'listen': [('127.0.0.1', 6667)],
    'motd': ['Welcome to my humble server!',
             'This server is a test version of tornadoirc',
             'If you find any issues, please report to the developer.'],
    'nicklen': 30,
    'pinginterval': 60,
    'pingtimeout': 120,
}

##
# Profiling
##
profiling = True
