# Create your views here.

from logger.models import *

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.views.generic.list_detail import object_list


@login_required
def index(request, page=1, template='logger/log_list.html'):
	if not request.user.is_staff:
		return redirect_to_login(request.META.get('PATH_INFO','/admin'))

	q = request.GET.get('q', '')
	c = request.GET.get('c', '')
	if q.__len__():
		logs = Log.objects.filter(
				statement__contains=q).order_by('-time')
	elif c.__len__():
		logs = Log.objects.filter(
				session__context__contains=c).order_by('-time')
	else:
		logs = Log.objects.all().order_by('-time')

	if ('csv' == request.GET.get('format', '')):	# rfc4180
		return render_to_response('logger/log_list.csv', {'logs':logs},
				mimetype='text/csv')

	return object_list(request, queryset=logs, paginate_by=20, page=page,
			extra_context = {'query': q, 'context': c })



def insert(request):
	st = request.POST.get('statement', '')
	pr = request.POST.get('priority', 'L')
	se = request.POST.get('serial', 0)
	uu = request.POST.get('session', 'new')

	content = "%s,%s,%s,%s" % (st,pr,se,uu)
	print content

	if (uu == 'new' or uu == ''):
		ho = request.META.get('REMOTE_ADDR', '0.0.0.0')
		co = request.POST.get('context', '')
		session = Session(context=co)
		session.link_to(ho)
		session.save()
	else:
		session = Session.objects.filter(uuid=uu)[0]

	log = Log(session=session, statement=st, serial=se, priority=pr)
	log.save()

	content = "%s %s xxx%s" % (str(session), se, content)
	return HttpResponse(content=content, status=202)



@login_required
def session_detail(request, session_id, template='logger/session_detail.html'):
	if not request.user.is_staff:
		return redirect_to_login(request.META.get('PATH_INFO','/admin'))

	if session_id:
		sess = Session.objects.get(pk=session_id)
	else:
		return HttpResponse(status=404)

	logs = Log.objects.filter(session=sess)

	log_filter = request.GET.get('filter', 'client')
	if log_filter == 'info':
		log_filter = '_INFO'
	elif log_filter == 'server':
		log_filter = '<<<'
	elif log_filter == 'client':
		log_filter = '>>>'
	elif log_filter == 'full':
		log_filter = ''

	logs = logs.filter(statement__contains=log_filter).order_by('time')

	return render_to_response(template,
			{'session':sess, 'logs':logs},
			context_instance=RequestContext(request),
			)
