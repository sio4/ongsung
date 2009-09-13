from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', 'queman.views.index'),
	# default CRUD
	(r'^create/$', 'queman.views.create'),			# POST, create
	(r'^(?P<queue_id>\d+)/$', 'queman.views.detail'),	# GET, read
	(r'^(?P<queue_id>\d+)/update/$', 'queman.views.update'),	# PUT
	#(r'^(?P<queue_id>\d+)/delete/$', 'queman.views.update'),
	# for worker node
	#(r'^(?P<queue_id>\d+)/take/$', 'queman.views.take'),
	#(r'^(?P<queue_id>\d+)/done/$', 'queman.views.done'),
	#(r'^(?P<queue_id>\d+)/drop/$', 'queman.views.drop'),
	#(r'^statics/(?P<path>.*)$', 'django.views.static.serve',
	#	{'document_root': 'queman/statics/'}),

)
