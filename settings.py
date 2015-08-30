# coding: utf-8

##
# Process
##
process_name = 'tornadoircd'

##
# IRCd
##
ircd = {
    'servername': 'irc.testnetwork.org',
    'listen': [('127.0.0.1', 6667)],
    'motd': ['Welcome to my humble server!',
             'This server is a test version of tornadoirc',
             'If you find any issues, please report to the developer.'],
}

##
# User
##
user = {
    'nicklen': 30,
}


##
# Local time
##
import pytz
localtime = pytz.timezone('America/Sao_Paulo')

##
# Timestamp range (current value: years of 2015 to 2096)
##
timestamp_range = {'min': 1420077600, 'max': 4000000000}

##
# Profiling
##
profiling = True
