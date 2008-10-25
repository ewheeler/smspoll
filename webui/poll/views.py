#!/usr/bin/env python
# vim: noet

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from models import *
from utils import *


def dashboard(req):
	
	return render_to_response("dashboard.html", { "questions": Question.objects.all() })


def add_question(req):
	if req.method == "POST":
		post = querydict_to_dict(req.POST)
		
		# replace the key/values of the six <select> boxes (D/M/Y for start+end) with a single date field
		post["start"] = "%4d-%02d-%02d" % (int(post.pop("start-year")), int(post.pop("start-month")), int(post.pop("start-day")))
		post["end"]   = "%4d-%02d-%02d" % (int(post.pop("end-year")),   int(post.pop("end-month")), int(post.pop("end-day")))		
		
		# create the object and redirect to dashboard
		# no error checking for now, except django's
		# model and database constraints
		Question(**post).save()
		return HttpResponseRedirect("/")
	
	# render the ADD form
	return render_to_response("add-question.html")


def message_log(req):
	return render_to_response("message-log.html")
