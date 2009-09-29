from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from logger.models import Log
from wall.models import Bookmark


page = { 'paginate_by': 20, }
all_logs = { 'queryset': Log.objects.all(), 'paginate_by': 20, }
by_session = lambda kwargs: Log.objects.filter(session=kwargs['session'])


urlpatterns = patterns('',
	(r'^$', 'wall.views.index'),
	(r'^logs/(.*)$', 'logger.views.index'),
	#(r'^logs/', object_list, dict(page, queryset=Log.objects.all())),
	(r'^session/(?P<session_id>\w+)/$', 'logger.views.session_detail'),
	#(r'^session/([^/]+)/$', 'logger.views.session_detail'),
)


