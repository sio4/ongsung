from django.conf.urls.defaults import *
from django.views.generic.create_update import delete_object

from blog.models import Page

urlpatterns = patterns('',
	(r'^page/create/$', 'blog.views.page_create'),
	(r'^page/$', 'blog.views.page_index'),
  (r'^page/(?P<object_id>\w+)/delete/$', delete_object,
		{'model':Page,'post_delete_redirect':'/blog/page/'}),
  (r'^page/(?P<page_id>\w+)/update/$', 'blog.views.page_update')

	# default CRUD
	#(r'^insert/$', 'logger.views.insert'),
	#(r'^(?P<queue_id>\d+)/$', 'queman.views.detail'),	# GET, read
	#(r'^(?P<queue_id>\d+)/update/$', 'queman.views.update'),	# PUT
)
