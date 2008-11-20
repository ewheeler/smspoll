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


	# SUBSCRIBE -----------------------------------------------------------------
	kw.prefix = ["subscribe", "join"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def subscribe(self, caller, blah=None):
		res = self.__get(Respondant, phone=caller)
		if res: 
			res.is_active = True 
			res.save()
			self.respond(STR["resubscribe"])
		else:
			res = Respondant.create(phone=caller, is_active=True)
			self.respond(STR["subscribe"])


	# UNSUBSCRIBE -----------------------------------------------------------------
	kw.prefix = ["unsubscribe", "leave", "stop", "exit"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def unsubscribe(self, caller, blah=None):
		res = self.__get(Respondant, phone=caller)
		if res: 
			res.is_active = False
			res.save()
			self.respond(STR["unsubscribe"])
		else:
			raise CallerError(STR["unsubscribe_unknown"])


	# CONVERSATIONAL  ------------------------------------------------------------
	kw.prefix = ["ok", "thanks", "thank you"]
	
	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_welc(self, caller):
		self.respond(STR["conv_welc"])
	

	kw.prefix = ["hi", "hello", "howdy", "whats up"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_greet(self, caller, whatever=None):
		self.respond(STR["conv_greet"])


	kw.prefix = ["fuck", "damn", "shit", "bitch"]

	@kw.blank()
	@kw("(whatever)")
	@kw.invalid()
	def conv_swear(self, caller, whatever=None):
			self.respond(STR["conv_swear"])


	# LOGGING -----------------------------------------------------------------
	
	# always called by smsapp, to log
	# without interfereing with dispatch
	def before_incoming(self, caller, msg):
		
		# we will log the respondant, if we can identify
		# them by their number. otherwise, log the number
		res = self.__get(Respondant, phone=caller)
		if res is None: ph = caller
		else: ph = None
		
		# create a new log entry
		Message.objects.create(
			is_outgoing=False,
			respondant=res,
			message=msg)
	
	
	# as above...
	def before_outgoing(self, recipient, msg):
		
		# we will log the monitor, if we can identify
		# them by their number. otherwise, log the number
		res = self.__get(Respondant, phone=recipient)
		if res is None: ph = recipient
		else: ph = None
		
		# create a new log entry
		Message.objects.create(
			is_outgoing=True,
			respondant=res,
			message=msg)


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)
