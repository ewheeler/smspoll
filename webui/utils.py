#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *

from poll.models import *

def broadcast_question(question):
	# lets send with pykannel!
	sender = kannel.SmsSender("user", "password")

	# gather active respondants
	respondants = Respondant.objects.filter(is_active=True)
	sending = 0

	# message to be blasted
	broadcast = question.text

	# unless this is a free text question,
	# add the answer choices to the broadcast message
	if question.type != 'F':
		answers = Answer.objects.filter(question=question.pk)
		for a in answers:
			broadcast = broadcast + '\n ' + a.choice + ' - ' + a.text

	# blast the broadcast message to our active respondants
	# and increment the counter
	for r in respondants:
		sender.send(r.phone, broadcast)
		sending += 1
		print 'Blasted to %d of %d numbers...' % (sending, len(respondants))

	# save number broadcasted to db
	question.sent_to = sending
	question.save()

	return 'Blasted %s to %d numbers with %d failures' % (broadcast, sending, (len(respondants) - sending))


def querydict_to_dict(qd):
	if isinstance(qd, dict): return qd
	return dict((str(k), v) for k, v in qd.iteritems())




from django.db.models.fields import DateField

def object_from_querydict(model, qd, suffix=""):
	dict = querydict_to_dict(qd)
	obj_dict = {}
	
	# iterate the fields in the model, building
	# a dict of matching POSTed values as we go
	for field in model._meta.fields:
		fn = field.name + suffix
		
		# if an exact match was
		# POSTed, then use that
		if fn in dict:
			obj_dict[fn] = dict[fn]
		
		# date fields can be provided as three
		# separate values, so D/M/Y <select>
		# elements can easily be used
		elif isinstance(field, DateField):
			try:
				obj_dict[fn] = "%4d-%02d-%02d" % (
					int(dict[fn+"-year"]),
					int(dict[fn+"-month"]),
					int(dict[fn+"-day"]))
			
			# choo choooo...
			# all aboard the fail train
			except KeyError:
				pass
	
	# create the instance based upon
	# the fields we just extracted
	return model(**obj_dict)

