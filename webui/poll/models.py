#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 

class Respondant(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	is_active = models.BooleanField()

	def __unicode__(self):
		return self.phone


class Message(models.Model):
	respondant = models.ForeignKey(Respondant, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()

	# todo: what is this for? the screen log?
	def __unicode__(self):
		if self.is_outgoing: dir = ">>"
		else:                dir = "<<"
		return "%s %s: %s" % (dir, self.respondant, self.message)


class Question(models.Model):
	QUESTION_TYPES = (
		('F', 'Free text'),
		('B', 'Boolean'),
		('M', 'Multiple choice'),
	)

	start = models.DateTimeField()
	end = models.DateTimeField()
	text = models.CharField(max_length=160)
	type = models.CharField(max_length=1, choices=QUESTION_TYPES)

	def __unicode__(self):
		return self.text


class Response(models.Model):
	respondant = models.ForeignKey(Respondant, blank=True, null=True)
	question = models.ForeignKey(Question, blank=True, null=True)
	message = models.ForeignKey(Message, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_unparseable = models.BooleanField()

	def __unicode__(self):
		return self.text