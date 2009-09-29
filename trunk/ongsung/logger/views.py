# Create your views here.

from logger.models import *

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.views.generic.list_detail import object_list


def index(request, page=1, template='logger/log_list.html'):
	q = request.GET.get('q', '')
	c = request.GET.get('c', '')
	if q is not '':
		logs = Log.objects.filter(statement__contains=q)
	elif c is not '':
		logs = Log.objects.filter(session__context__contains=c)
	else:
		logs = Log.objects.all()

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



def session_detail(request, session_id, template='logger/session_detail.html'):
	if session_id:
		sess = Session.objects.get(pk=session_id)
	else:
		return HttpResponse(status=404)

	logs = Log.objects.filter(session=sess)

	return render_to_response(template, {'session':sess, 'logs':logs})
