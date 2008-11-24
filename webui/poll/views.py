#!/usr/bin/env python
# vim: noet

import os, sys
from datetime import date, datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404

from webui.poll.models import *

from pygooglechart import SimpleLineChart, Axis, PieChart2D, StackedVerticalBarChart

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))

def graph_entries(q):
	question = get_object_or_404(Question, pk=q.pk)
	answers = Answer.objects.filter(question=question)
	if answers:
		if len(answers) > 2:
			return graph_multiple_choice(question)
		if len(answers) == 2:
			return graph_boolean(question)
	else:
		return graph_free_text(question)


def graph_multiple_choice(q):
	question = get_object_or_404(Question, pk=q.pk)
	answers = Answer.objects.filter(question=question)
	choices = { " " : 0}
	choices = choices.fromkeys(xrange(len(answers)), 0)

	entries = Entry.objects.filter(question=question,\
					is_unparseable=False)

	for e in entries:
		if int(e.text) in choices:
			choices[int(e.text)] += 10

	long_answers = []
	for a in answers:
		long_answers.append(a.text)

	bar = StackedVerticalBarChart(600,200)
	bar.set_colours(['4d89f9','c6d9fd'])
	bar.add_data(choices.values())
	bar.set_axis_labels(Axis.BOTTOM, long_answers)
	bar.download('poll/graphs/multiple_choice.png')
	
	return 'saved multiple_choice.png'


def graph_boolean(q):
	return 'called graph_boolean'	


def graph_free_text(q):
	return 'called graph_free_text'
