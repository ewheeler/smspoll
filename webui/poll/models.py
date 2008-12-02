#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
from datetime import date

class Respondant(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	is_active = models.BooleanField()

	def __unicode__(self):
		return self.phone
	
	@classmethod
	def subscribe(klass, caller, active=True):
		created = False
		
		try:
			# attempt to reactivate an
			# unsubscribed respondant
			r = klass.objects.get(phone=caller)
			r.is_active = active
			r.save()
		
		# no existing respondant, so create
		# a new, pre-activated, respondant
		except ObjectDoesNotExist:
			r = klass.objects.create(phone=caller, is_active=active)
			created = True
		
		# always return the object, with a bool
		# "created" flat like get_or_create
		return (r, created)
	
	@classmethod
	def unsubscribe(klass, caller):
		
		# recycle the "subscribe" function to
		# create and deactivate the respondant
		return klass.subscribe(caller, False)
		

class Message(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()

	def __unicode__(self):
		return self.text

class Question(models.Model):
	QUESTION_TYPES = (
		('F', 'Free text'),
		('B', 'Boolean'),
		('M', 'Multiple choice'),
	)

	start = models.DateField()
	end = models.DateField()
	text = models.CharField(max_length=160)
	type = models.CharField(max_length=1, choices=QUESTION_TYPES)
	sent_to = models.IntegerField(blank=True, null=True)

	def __unicode__(self):
		return self.text

	@staticmethod
	def current():
		today = date.today()
		
		# fetch all of the questions with dates spanning today. the
		# app should prevent there being more than one question active
		# on a single day, but since django 1.0 doesn't have model
		# validation, it's entirely possible
		active = Question.objects.filter(
			start__lte=today,
			end__gte=today
		).order_by('-end')
		
		# it's okay if nothing is active today
		# return None to prompt some other view
		if len(active) == 0: return None
		
		# othewise, return the first active question.
		# todo: warn or fix if multiple Qs are active
		else: return active[0]


class Answer(models.Model):
	question = models.ForeignKey(Question)
	text = models.CharField(max_length=30)
	choice = models.CharField(max_length=1)

	def __unicode__(self):
		return "(%s) %s" % (self.choice, self.text)


class Entry(models.Model):
	respondant = models.ForeignKey(Respondant, blank=True, null=True)
	question = models.ForeignKey(Question, blank=True, null=True)
	message = models.ForeignKey(Message, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_unparseable = models.BooleanField()
	moderated = models.BooleanField()

	def __unicode__(self):
		return self.text
	
	def meta_data(self):
		return "%s on %s at %s" % (
			self.respondant.phone,
			self.time.strftime("%d/%m"),
			self.time.strftime("%H:%M"))
	
	class Meta:
		verbose_name_plural="Entries"
