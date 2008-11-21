#!/usr/bin/env python
# vim: noet

from datetime import date, datetime

from webui.poll.models import *
from webui.utils import *

def dashboard(request):
	current_question = Question.objects.filter(
						end__lt=date.today())\
						.order_by('-end')[0]
