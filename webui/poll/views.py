#!/usr/bin/env python
# vim: noet
import os, sys
from datetime import datetime, date, timedelta
from pygooglechart import SimpleLineChart, Axis, PieChart2D, StackedVerticalBarChart

from django.views.decorators.http import require_POST
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.db import IntegrityError

from models import *
from utils import *

# craziness to get the graphs to save in the right spot
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, '..'))

# path, from above craziness, to graphs directory
GRAPH_DIR = 'poll/graphs/'

# graph sizes to generate (big & thumb)
GRAPH_SIZES = ['500', '240']


def golden(width):
	return int(width/1.6180339887498948482)


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
	# by the backend, but not moderated or parsed
	if ques: entries = ques.entry_set.all()
	else: entries = []

	return render_to_response("dashboard.html", {
		"question": ques,
		"previous": prev,
		"entries": entries,
		"tab": "dashboard"
	})


def add_question(req):
	
	# if we are POSTing, create the object
	# (and children) before redirecting
	if req.method == "POST":
		p = req.POST
		try:
			# extract the date range from the query dict
			start_str = "%4d-%02d-%02d" % (int(p["start-year"]), int(p["start-month"]), int(p["start-day"]))
			end_str   = "%4d-%02d-%02d" % (int(p["end-year"]), int(p["end-month"]), int(p["end-day"]))
			
			# before saving, check that the dates are
			# available (although this should have already been
			# done on the client side by ajax, we must check)
			avail = is_available(None, start_str, end_str)
			if isinstance(avail, HttpResponseServerError):
				return avail
			
			q = object_from_querydict(Question, req.POST)
			q.save()
			
			# for multiple choice questions, also
			# create the linked Answer objects
			if q.type == "M":
				for n in range(1, 5):
					object_from_querydict(
						Answer,
						req.POST,
						{ "question": q },
						("-%s" % n)
					).save()
			
			# redirect to the dashboard
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


def is_available(req, from_str, to_str):
	delta = timedelta(1)
	fmt = "%Y-%m-%d"

	# parse into date objects
	day = datetime.strptime(from_str, fmt)
	last = datetime.strptime(to_str, fmt)
	
	taken = []
	while(day <= last):
		q = Question.on(day)
		if q is not None:
			taken.append((q, day))
		
		# next day
		day += delta
	
	# if any of the days we just iterated were
	# already taken by an existing question,
	# then compile and return a list of errors
	# to be displayed by ajax (or seen by a low-
	# tech or non-js browser)
	if len(taken):
		errs = ["  %s by %s" % (day.strftime(fmt), q) for q, day in taken]
		return HttpResponseServerError(
			"The following dates are already reserved:\n" + "\n".join(errs),
			content_type="text/plain")
	
	# no dates were taken, so this range is fine
	return HttpResponse("OK", content_type="text/plain")
		

	
	



@require_POST
def moderate(req, id, status):
	ent = get_object_or_404(Entry, pk=id)
	
	# update the "moderated" status,
	# which makes this a regular entry
	if (status == "win"):
		ent.moderated = True
		ent.save()
	
	# remove bad entries from the db
	# altogether. we'll still have the
	# Message object to refer to
	elif (status == "fail"):
		ent.delete()
	
	# a really boring response. the HTTP code
	# is all we really need on the client side
	return HttpResponse("OK", content_type="text/plain")


@require_POST
def correction(req, id):

	# update the Entry and Message objects
	ent = get_object_or_404(Entry, pk=id)
	ent.message.text = req.POST["text"]
	ent.save()
	
	# run the correction back through the parser,
	# and throw an http500 (mostly to be caught
	# by ajax) if it failed again
	if not parse_message(ent, ent.question):
		return HttpResponseServerError(
			"Entry was still unparseable",
			content_type="text/plain")
	
	# no fail = success!
	return HttpResponse("OK", content_type="text/plain")


def message_log(req):
	return render_to_response("message-log.html", {
		"messages": Message.objects.all().order_by("-pk"),
		"tab": "log"
	})


def graph_entries(q):
	question = get_object_or_404(Question, pk=q.pk)

	# generate question participation graph
	print graph_participation(q)

	# figure out what kind of question we have
	# and generate the appropriate graph
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

	# look up how many people were asked this question
	# and make a ratio
	# if None, use 0
	if question.sent_to:
		participation = float(len(entries))/float(question.sent_to)
	else: 
		participation = 0.0

	# normalize data
	pending = 100 * (1.0 - participation)
	participants = 100 - pending 

	for size in GRAPH_SIZES:
		# configure and save the graph
		pie = PieChart2D(int(size), golden(int(size)))
		pie.add_data([pending, participants])
		pie.set_legend(['Pending' , 'Respondants'])
		pie.set_colours(['0091C7','0FBBD0'])
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-participation.png'
		pie.download(filename)
		print 'saved ' + filename

	return 'graphed participation ' + question.text


def graph_multiple_choice(q):
	question = get_object_or_404(Question, pk=q.pk)
	
	# collect answers to this question
	answers = Answer.objects.filter(question=question).order_by('choice')

	# old code for handling any number of choices
	# choices = { " " : 0 }
	# choices = choices.fromkeys(xrange(len(answers)), 0)

	# hardcode of four choices since ui limits to four
	choices = { 1 : 0, 2 : 0, 3 : 0, 4 : 0 }
	
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

	for size in GRAPH_SIZES:
		# configure and save the graph
		bar = StackedVerticalBarChart(int(size), golden(int(size)))
		bar.set_colours(['0091C7','0FBBD0'])
		bar.add_data(choices.values())
		bar.set_bar_width(int(int(size)/(len(choices)+1)))
		index = bar.set_axis_labels(Axis.BOTTOM, long_answers)
		bar.set_axis_style(index, '202020', font_size=9, alignment=0)
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-entries.png'
		bar.download(filename)
		print 'saved ' + filename
	
	return 'graphed entries ' + question.text


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
	
	# only two choices (unless we accept maybies)
	long_answers = ["Nay", "Yea"]

	for size in GRAPH_SIZES:
		# configure and save the graph
		pie = PieChart2D(int(size), golden(int(size)))
		# TODO normalize values
		pie.add_data(choices.values())
		pie.set_legend(long_answers)
		pie.set_colours(['0091C7','0FBBD0'])
		filename = GRAPH_DIR + str(question.pk) + '-' + size + '-entries.png'
		pie.download(filename)
		print 'saved ' + filename
	
	return 'graphed entries ' + question.text


def graph_free_text(q):
	return 'called graph_free_text'
