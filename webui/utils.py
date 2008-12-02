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

def querydict_to_dict(qd):
	return dict((str(k), v) for k, v in qd.iteritems())




from django.db.models.fields import DateField

def object_from_querydict(model, qd, other=None, suffix=""):
	dict = querydict_to_dict(qd)
	obj_dict = {}
	
	# if applicable, merge the 'other' dict,
	# which contains pre-filled values, not
	# from a query dict
	if other is not None:
		for k, v in other.iteritems():
			dict[str(k) + suffix] = v
	
	# iterate the fields in the model, building
	# a dict of matching POSTed values as we go
	for field in model._meta.fields:
		fn = field.name
		fns = fn + suffix
		
		# if an exact match was
		# POSTed, then use that
		if fns in dict:
			obj_dict[fn] = dict[fns]
		
		# date fields can be provided as three
		# separate values, so D/M/Y <select>
		# elements can easily be used
		elif isinstance(field, DateField):
			try:
				obj_dict[fn] = "%4d-%02d-%02d" % (
					int(dict[fns+"-year"]),
					int(dict[fns+"-month"]),
					int(dict[fns+"-day"]))
			
			# choo choooo...
			# all aboard the fail train
			except KeyError:
				pass
	
	# create the instance based upon
	# the fields we just extracted
	return model(**obj_dict)

