#!/usr/bin/env python
# vim: noet

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from models import *
from utils import *


def dashboard(req):
	return render_to_response("dashboard.html")


def add_question(req):
	if req.method == "POST":
		q = object_from_querydict(Question, req.POST)
		q.save()
		return HttpResponseRedirect("/")
	
	return render_to_response("add-question.html")


def message_log(req):
	return render_to_response("message-log.html")
