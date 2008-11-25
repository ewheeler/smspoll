import os

import poll.views as pv

# magic admin stuff (remove during prod)
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	# serve assets via django, during development
	(r'^assets/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/assets"}),

    (r'^graphs/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/poll/graphs"}),

	# poll views (move to poll/urls.py)
	(r'^$',    pv.dashboard),
	(r'^add$', pv.add_question),
	(r'^add-answer$', pv.add_answer),
	(r'^log$', pv.message_log),

    # enable the django magic admin
    (r'^admin/(.*)', admin.site.root),
)
