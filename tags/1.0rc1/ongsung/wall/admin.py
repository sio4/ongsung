from ongsung.wall.models import *
from django.contrib import admin

class ProtocolAdmin(admin.ModelAdmin):
	list_display = ('name','port','handler')
	list_filter = ['handler']

class DeviceAdmin(admin.ModelAdmin):
	list_display = ('name','addr','prot','port')
	list_filter = ['addr','prot']
	fields = ['name','addr','prot','port']

class BookmarkAdmin(admin.ModelAdmin):
	list_display = ('stared','user','device','last_date','count')
	list_filter = ['stared','user','device']

admin.site.register(Protocol,ProtocolAdmin)
admin.site.register(Device,DeviceAdmin)
admin.site.register(Bookmark,BookmarkAdmin)
