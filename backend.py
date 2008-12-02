#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
from datetime import date, datetime
from strings import ENGLISH as STR

# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from webui import settings
setup_environ(settings)

# import the django models, which should be movd
# somewhere sensible at the earliest opportunity
from webui.poll.models import *
from webui import utils


class App(SmsApplication):
	kw = SmsKeywords()

	def __get(self, model, **kwargs):
		try:
			# attempt to fetch the object
			return model.objects.get(**kwargs)
		
		# no objects or multiple objects found (in the latter case,
		# something is probably broken, so perhaps we should warn)
		except (ObjectDoesNotExist, MultipleObjectsReturned):
			return None


	# SUBSCRIBE ---------------------------------------------------------------
	
	kw.prefix = ["subscribe", "join"]

	@kw.blank()
	@kw("(whatever)")
	def subscribe(self, caller, blah=None):
		r, created = Respondant.subscribe(caller)
		
		# acknowledge with an appropriate message
		if created: self.respond(STR["subscribe"])
		else: self.respond(STR["resubscribe"])
	
	
	# UNSUBSCRIBE -------------------------------------------------------------
	
	kw.prefix = ["unsubscribe", "leave", "stop", "exit"]

	@kw.blank()
	@kw("(whatever)")
	def unsubscribe(self, caller, blah=None):
		r, created = Respondant.unsubscribe(caller)
		self.respond(STR["unsubscribe"])
	
	
	# SUBMIT AN ANSWER --------------------------------------------------------

	def incoming_sms(self, caller, msg):
		# ensure that the caller is subscribed
		r, created = Respondant.subscribe(caller)
		
		# if no question is currently running, then
		# we can effectively ignore the incoming sms,
		# but should notify the caller anyway
		ques = Question.current()
		if ques is None: self.respond(STR["no_question"])
		
		# try to parse the message
		parsed = utils.parse_message(self.log_msg, ques)

		# send an appropriate response to the caller
		if parsed:	self.respond(STR["thanks"])
		else:       self.respond(STR["thanks_unparseable"])


	# LOGGING -----------------------------------------------------------------
	
	# always called by smsapp, to log
	# without interfereing with dispatch
	def before_incoming(self, caller, msg):
		
		# create a new log entry
		self.log_msg =\
		Message.objects.create(
			is_outgoing=False,
			phone=caller,
			text=msg)

	
	# as above...
	def before_outgoing(self, caller, msg):
		
		# create a new log entry
		Message.objects.create(
			is_outgoing=True,
			phone=caller,
			text=msg)


# run the application
app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)
