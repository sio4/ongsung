# Create your views here.
from wall.models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

import os
import datetime
import httplib, urllib
import time


@login_required
def index(request, template_name='wall/index.html'):
	recent = Bookmark.objects.filter(user=request.user).order_by('-last_date')[:5]
	top = Bookmark.objects.filter(user=request.user).order_by('-count')[:5]
	stared = Bookmark.objects.filter(user=request.user,stared=True).order_by('-count')[:5]
	protocol = Protocol.objects.all()

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
				'protocol':protocol,
				'launch':launch})

@login_required
def connect(request, device_id=None):
	user = request.user
	current_datetime = datetime.datetime.now()
	message = ''
	error = ''

	if request.META['REQUEST_METHOD'] == 'GET' and device_id:
		d = Device.objects.get(pk=device_id)
	elif request.META['REQUEST_METHOD'] == 'POST':
		req_addr = request.POST.get('addr', '').strip()
		req_port = request.POST.get('port', None).strip()
		req_prot = request.POST.get('prot', 'telnet').strip()

		if req_addr == '':
			error += "destination address is not given. ignore."
			request.session['error'] = error
			return HttpResponseRedirect(reverse('wall.views.index'))

		try:
			d = Device.objects.filter(addr=req_addr)[0]
			# FIXME Q:if we need more than one protocol for one host?
		except:
			# register device on-the-fly
			prot=Protocol.objects.get(name=req_prot)
			d = Device(name=req_addr,addr=req_addr,prot=prot)
			if req_port:
				d.port = int(req_port)
			d.save()
			message += ' New machine %s registered. ' % (d.addr)

	### now prepare to invoke tunnel:
	addr = d.addr
	if d.port:
		port = d.port
	else:
		port = d.prot.port
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

	command = 'ongsung-tunnel %s %s %s' % (addr, port,
			request.META['REMOTE_ADDR'])

	# insert job into queue...
	params = urllib.urlencode({'command':command, 'feature':'telnet',
		'user':request.user.id})
	headers = {"Content-type":"application/x-www-form-urlencoded"}
	conn = httplib.HTTPConnection(request.META.get('HTTP_HOST','localhost'))
	conn.request("POST", "/q/create/", params, headers)
	response = conn.getresponse()
	data = response.read()
	conn.close()

	if response.status != 200:
		error += 'job insertion failed.'
		error += ' %s %s' % (response.status, response.reason)
		request.session['error'] = error
		return HttpResponseRedirect(reverse('wall.views.index'))


	# XXX temporary, i am the worker and i know what do i do.
	# it must be removed from here after workers are implemented.
	# service port must be checked and generated by worker.
	serv_host = request.META['HTTP_HOST'].split(':')[0]
	serv_port = int(request.META['REMOTE_PORT']) + 3840
	context = '%s@%s' % (user.username, addr)
	command_temp = 'ongsung-tunnel %s %s %s %s %s' % (context,
			addr, port, request.META['REMOTE_ADDR'], serv_port)

	os.system(command_temp)


	# waiting for worker attached and get connection info...
	# TODO now, just work around version without queman
	time.sleep(3)


	## temporary, just to me.
	request.session['launch'] = 'telnet://%s:%s' % (serv_host, serv_port)
	request.session['message'] = message
	print "service: %s" % command_temp
	print "service: %s" % command
	print "redirect to: %s" % request.session['launch']
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

