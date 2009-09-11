from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', 'wall.views.index'),
	(r'^connect/$', 'wall.views.connect'),
	(r'^device/(?P<device_id>\d+)/connect/$', 'wall.views.conn'),
	(r'^bookmark/(?P<bookmark_id>\d+)/stared/$', 'wall.views.stared'),
	(r'^(?P<task_id>\d+)/$', 'wall.views.index'),
	(r'^statics/(?P<path>.*)$', 'django.views.static.serve',
		{'document_root': 'wall/statics/'}),

)
