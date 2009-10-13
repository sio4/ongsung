# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.shortcuts import render_to_response

from django.contrib.auth.models import User, Group
from logger.models import Session



@login_required
def user_index(request, page=1, template='auth/user_list.html'):
	if not request.user.is_staff:
		return redirect_to_login(request.META.get('PATH_INFO','/admin'))

	id = request.GET.get('id', '')
	name = request.GET.get('name', '')
	if id.__len__():
		users = User.objects.filter(
				username__contains=id).order_by('username')
	elif name.__len__():
		users = User.objects.get(
				Q(first_name__contains=name) |
				Q(last_name__contains=name)
			)
	else:
		users = User.objects.all().order_by('username')

	if ('csv' == request.GET.get('format', '')):	# rfc4180
		return render_to_response('auth/user_list.csv', {'users':users},
				mimetype='text/csv')

	return object_list(request, queryset=users, paginate_by=20, page=page,
			extra_context = {'id': id, 'name': name })



def user_create(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.first_name = request.POST.get('first_name', '')
			user.last_name = request.POST.get('last_name', '')
			user.email = request.POST.get('email', '')
			user.is_active = True
			user.is_staff = False
			user.save()
			return HttpResponseRedirect(reverse('main.views.user_index'))
		else:
			return HttpResponseRedirect(reverse('main.views.user_index'))
	else:
		return HttpResponseRedirect(reverse('main.views.user_index'))



@login_required
def user_detail(request, user_id, template='auth/user_detail.html'):
	if user_id:
		user = User.objects.get(pk=user_id)
	else:
		return HttpResponse(status=404)

	sessions = Session.objects.filter(
			context__contains=user.username).order_by('-time')

	context = request.GET.get('context', '')
	if context.__len__():
		sessions = sessions.filter(context__contains=context)

	page = request.GET.get('page', '1')

	return object_list(request, queryset=sessions, paginate_by=5, page=page,
			extra_context = {'xuser': user, 'context':context })


