# Create your views here.

from queman.models import *
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseNotModified
from django.utils.feedgenerator import Rss201rev2Feed

# for quick method
from django.shortcuts import render_to_response
from django.template import RequestContext

### utilities
def rss_feed(request, queue_list):
	site_link = u'http://%s/q/' % request.META['HTTP_HOST']
	feed = Rss201rev2Feed(u"new job info", site_link, u'your new job' )
	for q in queue_list:
		link = site_link + str(q.id)
		feed.add_item(q.__unicode__(), link, q.owner.username,)
	response = HttpResponse(mimetype='application/xml')
	feed.write(response, 'utf-8')
	return  response


# quick method with template system
def render_xml(request, queue_list, template='queue.xml'):
	return render_to_response(template,
			{'queue_list':queue_list},
			context_instance=RequestContext(request),
			mimetype='text/xml')



def create(request):
	if request.POST.get('feature', '') == '':
		return HttpResponse(status=404)
	if request.POST.get('command', '') == '':
		return HttpResponse(status=404)
	if request.POST.get('user', '') == '':
		return HttpResponse(status=404)

	f = Feature.objects.filter(name=request.POST['feature'])[0]
	u = User.objects.get(pk=request.POST['user'])
	q = Queue(owner=u,feature=f,command=request.POST['command'])
	q.save()

	return render_xml(request, [q])

def detail(request, queue_id):
	return render_xml(request, [Queue.objects.get(pk=queue_id)])

def index(request):
	try:
		status = request.GET['status']
	except:
		status = ''
	if status != '':
		queue_list = Queue.objects.filter(status=status)
		queue_list = queue_list.order_by('-created_at')
	else:
		queue_list = Queue.objects.all().order_by('-created_at')
	return render_xml(request, queue_list)

def update(request, queue_id):
	q = Queue.objects.get(pk=queue_id)
	updated = False
	if request.GET.get('status', '') != '':
		q.status = request.GET['status']
		if q.status == 'R' and not q.started_at:
			q.started_at = datetime.datetime.now()
		elif q.status == 'D' and not q.finished_at:
			q.finished_at = datetime.datetime.now()
		updated = True
	if request.GET.get('worker', '') != '':
		q.worker = Worker.objects.get(pk=request.GET['worker'])
		updated = True
	if request.GET.get('info', '') != '':
		q.info = request.GET['info']
		updated = True

	if updated:
		q.updated_at = datetime.datetime.now()
		q.save()
		return render_xml(request, [q])
	return HttpResponseNotModified()





