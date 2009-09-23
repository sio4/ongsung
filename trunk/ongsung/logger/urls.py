from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', 'logger.views.index'),
	# default CRUD
	(r'^insert/$', 'logger.views.insert'),
	#(r'^add/$', 'logger.views.create'),			# POST, create
	#(r'^(?P<queue_id>\d+)/$', 'queman.views.detail'),	# GET, read
	#(r'^(?P<queue_id>\d+)/update/$', 'queman.views.update'),	# PUT
)
