from django.template import Library
from poll.models import *
register = Library()


# UTIL -----------------------------------------------------

def rand():
	from random import randint
	return randint(111111,999999)


# INCLUSION TAGS --------------------------------------------

from django.utils.dates import MONTHS
import time

@register.inclusion_tag("partials/date-selector.html")
def date_selector(prefix):
	now = time.localtime()
	
	return {
		"prefix": prefix,
		"days":   list((d, d==now.tm_mday) for d in range(1, 32)),
		"months": list((unicode(MONTHS[m]), m==now.tm_mon) for m in MONTHS.iterkeys()),
		"years":  list((y, y==now.tm_year) for y in range(now.tm_year, now.tm_year+5))
	}


def question_data(question):
	from django.utils import simplejson
	data = [(answer.text, votes) for answer, votes in question.results()]
	return { "question" : question, "rnd": rand(), "data": simplejson.dumps(data) }

@register.inclusion_tag("partials/question-summary.html")
def question_summary(question):	
	return question_data(question)

@register.inclusion_tag("partials/question-full.html")
def question_full(question):
	return question_data(question)


@register.inclusion_tag("partials/add-answer.html")
def add_answer(number):
	return { "questions" : Question.objects.all(),\
				"number" : number }


# SIMPLE TAGS -----------------------------------------------

@register.simple_tag
def num_unparseables():
	num = len(Entry.objects.filter(is_unparseable=True))
	if num > 0: return "(%d)" % num
	else:       return ""
