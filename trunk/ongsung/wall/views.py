# Create your views here.
from wall.models import *

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

import os

def index(request, template_name='wall/index.html'):
	recent = Bookmark.objects.all().order_by('-last_date')[:10]
	stared = Bookmark.objects.filter(stared=True).order_by('-count')[:10]
	return render_to_response(template_name,
			{'recent':recent, 'stared':stared})

def connect(request):
	os.system('ongsung-tunnel %s' % request.POST['addr'])
	return HttpResponseRedirect('..')
