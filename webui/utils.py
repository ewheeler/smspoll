#!/usr/bin/env python
# vim: noet

#import kannel
#from smsapp import *

def blast_numbers(numbers, message):
	# blasts a message to a list of numbers
	sending = 0
	sender = kannel.SmsSender("user", "password")
	for n in numbers:
		sender.send(n, message)
		sending += 1
		print 'Blasted to %d of %d numbers...' % (sending, len(numbers))
        return 'Blasted %s to %d numbers with %d failures' % (message, sending, (len(numbers) - sending))

def object_from_querydict(klass, query_dict):
	
	str_dict = {}
	for key, value in query_dict.items():
		str_dict[str(key)] = value
	
	return klass(**str_dict)
