from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic.create_update import delete_object
from django.contrib.auth.models import User

from django.views.generic.list_detail import object_list
from logger.models import Log
from wall.models import Bookmark


page = { 'paginate_by': 20, }
all_logs = { 'queryset': Log.objects.all(), 'paginate_by': 20, }
by_session = lambda kwargs: Log.objects.filter(session=kwargs['session'])


urlpatterns = patterns('',
	(r'^$', redirect_to, {'url':'log/'}),
	(r'^log/(.*)$', 'logger.views.index'),
	#(r'^log/', object_list, dict(page, queryset=Log.objects.all())),
	(r'^session/(?P<session_id>\w+)/$', 'logger.views.session_detail'),
	#(r'^session/([^/]+)/$', 'logger.views.session_detail'),
	(r'^user/$', 'main.views.user_index'),
	(r'^user/create/$', 'main.views.user_create'),
	(r'^user/(?P<user_id>\w+)/$', 'main.views.user_detail'),
	(r'^user/(?P<object_id>\w+)/delete/$', delete_object,
		{'model':User,'post_delete_redirect':'/admin/user/'}),
)



