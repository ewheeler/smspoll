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

	# collect answers to this question
	answers = Answer.objects.filter(question=question)
	
	# figure out what kind of question we have
	# and make the appropriate graph
	if answers:
		if len(answers) > 2:
			return graph_multiple_choice(question)
		if len(answers) == 2:
			return graph_boolean(question)
	else:
		return graph_free_text(question)


def graph_multiple_choice(q):
	question = get_object_or_404(Question, pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question)

	# this is obnoxious but the best
	# way python will allow making a
	# dict from a list
	choices = { " " : 0}
	choices = choices.fromkeys(xrange(len(answers)), 0)

	# grab the parsed entries for this question
	entries = Entry.objects.filter(question=question,\
					is_unparseable=False)

	# i'm assuming here that the Entry.text is the
	# same thing as the Answer.choice, presumably
	# a number for each choice 1 through  n
	# 
	# iterate entries and tally the choices
	for e in entries:
		if int(e.text) in choices:
			choices[int(e.text)] += 1

	# collect the long, textual representation
	# of the answer choice for labelling the graph
	long_answers = []
	for a in answers:
		long_answers.append(a.text)

	# configure and save the graph
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
