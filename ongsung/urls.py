from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url':'/ongsung'}),
    (r'^admin/', include('main.urls')),
    (r'^ongsung/', include('wall.urls')),
    (r'^q/', include('queman.urls')),
    (r'^logger/', include('logger.urls')),
    (r'^blog/', include('blog.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^djadmin/(.*)', admin.site.root),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/password/$', 'django.contrib.auth.views.password_change',
			{ 'post_change_redirect':'/ongsung', }),
		(r'^accounts/profile/$', redirect_to, {'url':'/ongsung'}),
)
