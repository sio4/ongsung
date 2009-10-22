from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.list_detail import object_list
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object

from blog.models import Page,Roll

urlpatterns = patterns('',
	(r'^$', redirect_to, {'url':'page/'}),
	(r'^page/create/$', 'blog.views.page_create'),
	(r'^page/$', 'blog.views.page_index'),
	(r'^page/(?P<page_id>\w+)$', 'blog.views.page_index'),
	(r'^page/(?P<page_id>\w+)/edit/$', 'blog.views.page_edit'),
	(r'^page/(?P<object_id>\w+)/delete/$', delete_object,
		{'model':Page,'post_delete_redirect':'/blog/page/'}),
	(r'^page/(?P<page_id>\w+)/update/$', 'blog.views.page_update'),

	(r'^roll/$', 'blog.views.roll_index'),
	(r'^roll/create/$', create_object,
		{'model':Roll,'post_save_redirect':'/blog/roll/','login_required':True}),
	(r'^roll/(?P<object_id>\w+)/update/$', update_object,
		{'model':Roll,'post_save_redirect':'/blog/roll/','login_required':True}),
	(r'^roll/(?P<object_id>\w+)/delete/$', delete_object,
		{'model':Roll,'post_delete_redirect':'/blog/roll/','login_required':True}),
	#(r'^roll/(?P<roll_id>\w+)/(.*)$', 'blog.views.roll_detail'),
	# default CRUD
	#(r'^insert/$', 'logger.views.insert'),
	#(r'^(?P<queue_id>\d+)/$', 'queman.views.detail'),	# GET, read
	#(r'^(?P<queue_id>\d+)/update/$', 'queman.views.update'),	# PUT
)
