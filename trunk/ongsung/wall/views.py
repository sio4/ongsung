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
	recent = Bookmark.objects.filter(user=request.user).order_by('-last_date')[:5]
	top = Bookmark.objects.filter(user=request.user).order_by('-count')[:5]
	stared = Bookmark.objects.filter(user=request.user,stared=True).order_by('-count')[:5]

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

	try:
		launch = request.session['launch']
		request.session['launch'] = ''
	except:
		launch = ''

	return render_to_response(template_name,
			{'user':request.user, 'message':message, 'error':error,
				'recent':recent, 'stared':stared, 'top':top,
				'launch':launch})

@login_required
def connect(request, device_id=None):
	user = request.user
	current_datetime = datetime.datetime.now()
	message = ''
	error = ''

	# select device to connect if possible.
	try:
		if request.META['REQUEST_METHOD'] == 'POST':
			requested_addr = request.POST['addr'].split()[0]
			d = Device.objects.filter(addr=requested_addr)[0]
		elif request.META['REQUEST_METHOD'] == 'GET' and device_id:
			d = Device.objects.get(pk=device_id)
	except:
		error += "device selection error: unknown device or invalid."
		error += " contact to system administrator."

		request.session['message'] = message
		request.session['error'] = error
		return HttpResponseRedirect(reverse('wall.views.index'))

	addr = d.addr
	port = d.port
	message += "device(%s) selected." % d.name

	# update or create bookmark
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
	os.system('ongsung-tunnel %s %s' % (addr, port))

	server_addr = request.META['HTTP_HOST'].split(':')[0]
	request.session['launch'] = 'telnet://%s:%s' % (server_addr, 8000)
	request.session['message'] = message
	return HttpResponseRedirect(reverse('wall.views.index'))

# maybe this is my fault. i cannot write smart urls.py yet.
@login_required
def conn(request, device_id):
	return connect(request, device_id=device_id)

@login_required
def stared(request,bookmark_id):
	b = Bookmark.objects.get(pk=bookmark_id)

	if b.stared:
		b.stared = False
	else:
		b.stared = True
	b.save()
	
	return HttpResponseRedirect(reverse('wall.views.index'))

