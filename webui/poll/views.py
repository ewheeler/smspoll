#!/usr/bin/env python
# vim: noet

from django import http
from django.shortcuts import render_to_response, get_object_or_404

from models import *
from utils import *


def dashboard(req):
	return render_to_response("dashboard.html")


def add_question(req):
	return render_to_response("add-question.html")


def message_log(req):
	return render_to_response("message-log.html")
