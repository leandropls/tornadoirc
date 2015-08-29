# coding: utf-8

##
# Process
##
process_name = 'tornadoircd'

##
# IRCd
##
ircd = {
    'listen': [('127.0.0.1', 6667)]
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
