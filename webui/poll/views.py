#!/usr/bin/env python
# vim: noet
import os, sys
from pygooglechart import SimpleLineChart, Axis, PieChart2D, StackedVerticalBarChart

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.db import IntegrityError
from models import *
from utils import *

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))

GRAPH_DIR = 'poll/graphs/'
CURRENT_WIDTH = 500 

def dashboard(req, id=None):

	# if a pk was passed in the url, then
	# load that; otherwise, attempt to load
	# the currently-active question (or None)
	if id is None: ques = Question.current()
	else: ques = get_object_or_404(Question, pk=id)
	
	# the previous questions are always the same (for
	# now); TODO: show those adjacent to 'ques'
	prev = Question.objects.all()[:12]
	
	# show all of the answers related to this
	# question. these have already been filtered
	# by the backend, but not moderated
	if ques: entries = ques.entry_set.all()
	else: entries = []
	
	return render_to_response("dashboard.html", {
		"question": ques,
		"previous": prev,
		"entries": entries,
		"tab": "dashboard"
	})


def add_question(req):
	
	# if we are POSTing, create the object and redirect 
	# to the dashboard. no error checking for now, except
	# django's model and database constraints
	if req.method == "POST":
		try:
			print req.POST
			object_from_querydict(Question, req.POST).save()
			return HttpResponseRedirect("/")
		
		# something went wrong during object creation.
		# this should have been caught by javascript,
		# so halt with a low-tech error
		except IntegrityError, err:
			return HttpResponseServerError(
				"\n".join(list(e[1] for e in err)),
				content_type="text/plain")
	
	# otherwise, just render the ADD form
	return render_to_response("add-question.html", {
		"tab": "add-question"
	})


def add_answer(req):
	if req.method == "POST":
		post = querydict_to_dict(req.POST)

		post["question"] = Question.objects.get(pk=(int(post.pop("question"))))

		# create the object and redirect to dashboard
		# no error checking for now, except django's
		# model and database constraints
		Answer(**post).save()
		return HttpResponseRedirect("/")
	
	# render the ADD form
	return render_to_response("add-answer.html",\
		{ "questions" : Question.objects.all() })


def message_log(req):
	return render_to_response("message-log.html", {
		"messages": Message.objects.all().order_by("-pk")
	})


def graph_entries(q):
	question = get_object_or_404(Question, pk=q.pk)

	# generate question participation graph
	print graph_participation(q)

	# collect answers to this question
	answers = Answer.objects.filter(question=question)

	# figure out what kind of question we have
	# and generate the appropriate graph
	print question.type
	if question.type == 'M':
		return graph_multiple_choice(question)
	if question.type == 'B':
		return graph_boolean(question)
	if question.type == 'F':
		return graph_free_text(question)


def graph_participation(q):
	question = get_object_or_404(Question, pk=q.pk)

	# grab ALL entries for this question
	entries = Entry.objects.filter(question=question)

	# grab active respondants
	# TODO this will be inaccurate for older questions
	# and should find only respondants that were active
	# for this question
	all_respondants = Respondant.objects.filter(is_active=True)

	# normalize data
	pending = 100 * (1.0 - (float(len(entries))/float(len(all_respondants))))
	participants = 100 - pending 

	# configure and save the graph
	pie = PieChart2D(300, 100)
	pie.add_data([pending, participants])
	pie.set_legend(['Pending' , 'Respondants'])
	pie.set_colours(['0091C7','0FBBD0'])
	filename = GRAPH_DIR + str(question.pk) + '-participation.png'
	pie.download(filename)
	
	return 'saved ' + filename	


def graph_multiple_choice(q):
	question = get_object_or_404(Question, pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question)

	# this is obnoxious but the best
	# way python will allow making a
	# dict from a list
	choices = { " " : 0 }
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
	bar = StackedVerticalBarChart(CURRENT_WIDTH, golden(CURRENT_WIDTH))
	bar.set_colours(['0091C7','0FBBD0'])
	bar.add_data(choices.values())
	bar.set_bar_width(int(CURRENT_WIDTH/(len(choices)+1)))
	#bar.set_bar_width(50)
	index = bar.set_axis_labels(Axis.BOTTOM, long_answers)
	bar.set_axis_style(index, '202020', font_size=9, alignment=0)
	filename = GRAPH_DIR + str(question.pk) + '-graph.png'
	bar.download(filename)
	
	return 'saved ' + filename	

def golden(width):
	return int(width/1.6180339887498948482)


def graph_boolean(q):
	# this method is not very DRY with respect to
	# graph_multiple_choice
	# will probably combine these once we figure
	# out how they will be used

	question = get_object_or_404(Question, pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question)

	# only two choices unless we accept maybies
	choices = { 0 : 0, 1 : 0 }

	# grab the parsed entries for this question
	entries = Entry.objects.filter(question=question,\
					is_unparseable=False)

	# i'm assuming here that the Entry.text is the
	# same thing as the Answer.choice, presumably
	# 0 for false/no and 1 for true/yes
	# 
	# iterate entries and tally the choices
	for e in entries:
		if int(e.text) in choices:
			choices[int(e.text)] += 1
	
	# only two choices unless we accept maybies
	long_answers = ["Nay", "Yea"]

	# configure and save the graph
	pie = PieChart2D(CURRENT_WIDTH, golden(CURRENT_WIDTH))
	# TODO normalize values
	pie.add_data(choices.values())
	pie.set_legend(long_answers)
	pie.set_colours(['0091C7','0FBBD0'])
	filename = GRAPH_DIR + str(question.pk) + '-graph.png'
	pie.download(filename)
	
	return 'saved ' + filename	


def graph_free_text(q):
	return 'called graph_free_text'
