# Create your views here.
from wall.models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

import os
import datetime

@login_required
def index(request, template_name='wall/index.html'):
	recent = Bookmark.objects.all().order_by('-last_date')[:5]
	top = Bookmark.objects.all().order_by('-count')[:5]
	stared = Bookmark.objects.filter(stared=True).order_by('-count')[:5]

	try:
		message = request.session['message']
		request.session['message'] = ''
	except:
		message = ''

	try:
		error = request.session['error']
		request.session['error'] = ''
	except:
		error = ''

	return render_to_response(template_name,
			{'user':request.user, 'message':message, 'error':error,
				'recent':recent, 'stared':stared, 'top':top})

def connect(request):
	user = request.user
	requested_addr = request.POST['addr'].split()[0]
	current_datetime = datetime.datetime.now()

	try:
		d = Device.objects.filter(addr=requested_addr)[0]
		addr = d.addr
		port = d.port
		message = "device(%s) selected." % d.name
	except:
		error = "unknown device or invalid."
		error += " contact to system administrator."

		request.session['error'] = error
		return HttpResponseRedirect(reverse('wall.views.index'))

	try:
		b = Bookmark.objects.filter(user=user,device=d)[0]
		b.last_date = current_datetime
		b.count += 1
		message += ' visit again!'
	except:
		b = Bookmark(user=user,device=d,last_date=current_datetime)
		message += ' grad to see you!'
	b.save()

	# templorary
	port = 8000
	os.system('ongsung-tunnel %s %s &' % (addr, port))

	request.session['message'] = message
	return HttpResponseRedirect(reverse('wall.views.index'))

def stared(request,bookmark_id):
	return HttpResponseRedirect(reverse('wall.views.index'))

