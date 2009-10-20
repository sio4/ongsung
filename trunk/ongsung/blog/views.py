# Create your views here.
from django.contrib.auth.models import User
from blog.models import *

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

#from django.contrib.auth.models import User
from django.db.models import Q
import datetime

@login_required
def page_create(request):
	if not request.user.is_staff:
		return redirect_to_login(request.META.get('PATH_INFO','/admin'))

	if request.method == 'POST':
		subject = request.POST.get('subject', '')
		content = request.POST.get('content', '')

		p = Page(subject=subject, content=content, author=request.user)
		p.posted_at = datetime.datetime.now()
		p.save()

		tag_line = request.POST.get('tags', '')
		if tag_line.__len__():
			for tag in tag_line.split():
				t = p.tag_set.create(name=tag, page=p)
				t.save()

		return HttpResponseRedirect(reverse('blog.views.page_index'))
	else:
		return HttpResponseRedirect(reverse('blog.views.page_index'))


@login_required
def page_index(request, template='blog/page_list.html'):
	page = request.GET.get('page', 1)
	keyword = request.GET.get('keyword', '')
	if request.user.is_staff:
		objs = Page.objects.all()
	else:
		objs = Page.objects.filter(
				Q(author=request.user) | (Q(published=True, private=False))
				)
	if keyword.__len__():
		objs = objs.filter(
				content__contains=keyword)
	objs = objs.order_by('-sticky', '-posted_at')

	return object_list(request, queryset=objs, paginate_by=5, page=page,
			extra_context = {'query': keyword })


@login_required
def page_update(request, page_id):
	sticky = request.GET.get('sticky', '')
	private = request.GET.get('private', '')
	published = request.GET.get('published', '')
	date = request.GET.get('date', '')

	p = Page.objects.get(pk=page_id)

	if sticky.__len__() and sticky == 't':
		p.sticky  = True
	if sticky.__len__() and sticky == 'f':
		p.sticky  = False

	if private.__len__() and private == 't':
		p.private  = True
	if private.__len__() and private == 'f':
		p.private  = False

	if published.__len__() and published == 't':
		p.published  = True
	if published.__len__() and published == 'f':
		p.published  = False

	p.save()

	return HttpResponseRedirect(reverse('blog.views.page_index'))


from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def roll_index(request, template='blog/roll_list.html'):
	if not request.user.is_staff:
		return redirect_to_login(request.META.get('PATH_INFO','/admin'))

	objs = Roll.objects.all()

	return render_to_response(template,
			{'rolls':objs},
			context_instance=RequestContext(request),
			)

