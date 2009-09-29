from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from logger.models import Log

info_dict = {
	'queryset': Log.objects.all(),
	'template_name': 'logs.html',
}


urlpatterns = patterns('',
	(r'^$', 'logger.views.index'),
	(r'^logs/', object_list, info_dict),
	# default CRUD
	(r'^insert/$', 'logger.views.insert'),
	#(r'^add/$', 'logger.views.create'),			# POST, create
	#(r'^(?P<queue_id>\d+)/$', 'queman.views.detail'),	# GET, read
	#(r'^(?P<queue_id>\d+)/update/$', 'queman.views.update'),	# PUT
)
