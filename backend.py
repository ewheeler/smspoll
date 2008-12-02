#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
from datetime import date, datetime
from strings import ENGLISH as STR
import re

# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from webui import settings
setup_environ(settings)

# import the django models, which should be movd
# somewhere sensible at the earliest opportunity
from webui.poll.models import *

# regexes for matching boolean anwsers
B_REGEX_TRUE  = re.compile(r'^yes$', re.I)
B_REGEX_FALSE = re.compile(r'^no$', re.I)

# regexes for matching multiple choice answers
M_REGEX_1 = re.compile(r'^1$', re.I)
M_REGEX_2 = re.compile(r'^2$', re.I)
M_REGEX_3 = re.compile(r'^3$', re.I)
M_REGEX_4 = re.compile(r'^4$', re.I)


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
		
		# if we are logging free text answers,
		# just move the message straight into
		# the entries (unmoderated!)
		if ques.type == "F":
			Entry.objects.create(
				respondant=r,
				question=ques,
				message=self.log_msg,
				is_unparseable=False,
				moderated=False,
				text=msg)
			self.respond(STR["thanks"])

		# if we are logging boolean answers,
		# then we need to parse them based
		# on yes/no regexes
		if ques.type == "B":
			# assume the message is unparseable
			unparseable = True
			text = msg
			response = STR["thanks_unparseable"]
			
			# if yes matches, make a '1' entry
			if B_REGEX_TRUE.match(msg):
				text = '1'
				unparseable = False
				response = STR["thanks"]
			
			# if no matches, make a '0' entry
			elif B_REGEX_FALSE.match(msg):
				text = '0'
				unparseable = False
				response = STR["thanks"]

			Entry.objects.create(
				respondant=r,
				question=ques,
				message=self.log_msg,
				is_unparseable=True,
				moderated=True,
				text=msg)
			self.respond(response)

		# if we are logging multiple choice,
		# answers, then we need to parse
		# them based on our mc regexes
		if ques.type == "M":
			# assume the message is unparseable
			unparseable = True
			text = msg
			response = STR["thanks_unparseable"]

			# if 1 matches, make the entry
			if M_REGEX_1.match(msg):
				text = '1'
				unparseable = False
				response = STR["thanks"]
			# 2 matches...
			elif M_REGEX_2.match(msg):
				text = '2'
				unparseable = False
				response = STR["thanks"]
			# 3 matches...
			elif M_REGEX_3.match(msg):
				text = '3'
				unparseable = False
				response = STR["thanks"]
			# 4 matches...
			elif M_REGEX_4.match(msg):
				text = '4'
				unparseable = False
				response = STR["thanks"]
			
			Entry.objects.create(
				respondant=r,
				question=ques,
				message=self.log_msg,
				is_unparseable=True,
				moderated=True,
				text=msg)
			self.respond(response)


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


app = App(backend=kannel, sender_args=["user", "pass"])
app.run()


# wait for interrupt
while True: time.sleep(1)
