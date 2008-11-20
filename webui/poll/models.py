#!/usr/bin/env python
# vim: noet

from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 

class Respondant(models.Model):
	phone = models.CharField(max_length=30, blank=True, null=True)
	is_active = models.BooleanField()


class Message(models.Model):
	respondant = models.ForeignKey(Respondant, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=160)
	is_outgoing = models.BooleanField()

	# todo: what is this for? the screen log?
	def __unicode__(self):
		if self.is_outgoing: dir = ">>"
		else:                dir = "<<"
		return "%s %s: %s" % (dir, self.respondant, self.message)
