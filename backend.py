#!/usr/bin/env python
# vim: noet

import kannel
from smsapp import *
from datetime import date, datetime
from strings import ENGLISH as STR
import thread, time

# import the essentials of django
from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from webui import settings
setup_environ(settings)

# import the django models, which should be movd
# somewhere sensible at the earliest opportunity
from webui.poll.models import *
from webui import utils, graph




class SmsPoll(SmsApplication):
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
		if parsed:	
			graph.graph_entries(ques)
			self.respond(STR["thanks"])

		else:
			self.respond(STR["thanks_unparseable"])


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




# start up the application asap, so the broadcast
# threads have 'app' in their scope (just for logging)
app = SmsPoll(backend=kannel, sender_args=["user", "pass"])




# BROADCAST FUNCTIONS ----------------------------------------------------------

def broadcast_question(question):
	# lets send SMSs with pykannel!
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
		print '[broadcaster] Blasted to %d of %d numbers...' % (sending, len(respondants))

	# save number broadcasted to db
	question.sent_to = sending
	question.save()

	return '[broadcaster] Blasted %s to %d numbers with %d failures' % \
			(broadcast, sending, (len(respondants) - sending))


def broadcaster(seconds=60, wake_hour=8, sleep_hour=21):
	app.log("Starting Broadcaster...", "init")
	while True:
		
		# only broadcast while people are awake. otherwise, we'll be sending
		# people messages at 12:01AM, which probably won't go down so well
		hour = time.localtime()[3]
		if wake_hour < hour < sleep_hour:
			
			# if the current question has not been sent,
			# broadcaster will broadcast it
			q = Question.current()
			if q:
			
				# if this question hasn't been 'sent_to' anyone yet,
				# we can assume that it should be broadcast now
				if not q.sent_to:
					app.log("Broadcasting new question")
					broadcast_question(q)
				
				# already sent, so we have nothing to do
				# i don't think we really need to log this...
				#else: app.log("Current question was already broadcast")
				else: pass
			
			# when in production, there should probably ALWAYS
			# be an active question; otherwise, anyone texting
			# in will receive an error -- so highlight this
			# as a warning in the screen log
			else: app.log("No current question", "warn")
		
		# we are outside of waking hours, so do nothing
		else:
			app.log("Broadcast disabled from %d:00 to %d:00" %\
			        (sleep_hour, wake_hour))
		
		# wait until it's time
		# to check again (60s)
		time.sleep(seconds)




# MAIN APPLICATION LOOP --------------------------------------------------------

thread.start_new_thread(broadcaster, ())
app.run()

