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
	phone = models.CharField(max_length=30, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()

	# todo: what is this for? the screen log?
	def __unicode__(self):
		if self.is_outgoing: dir = ">>"
		else:                dir = "<<"
		return "%s %s: %s" % (dir, self.phone, self.text)


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

	def __unicode__(self):
		return self.text

	def _get_current_question(self):
		return  Question.objects.filter(
							end__lte=date.today())\
							.order_by('-end')[0]

	current_question = property(_get_current_question)


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

	class Meta:
		verbose_name_plural="Entries"
