from queman.models import *
from django.contrib import admin

class FeatureAdmin(admin.ModelAdmin):
	list_display = ('name','description')

class WorkerAdmin(admin.ModelAdmin):
	fields = ['name','addr','features']
	list_display = ('name','addr')
	list_filter = ['features']

class QueueAdmin(admin.ModelAdmin):
	fieldsets = [
		('Basic' ,{'fields':['owner','command','feature','status']}),
	]
	list_display = ('command','owner','feature','status','worker','info',
			'created_time', 'updated_time',
			'started_time', 'finished_time')
	list_filter = ['owner','feature','status','worker']

admin.site.register(Feature,FeatureAdmin)
admin.site.register(Worker,WorkerAdmin)
admin.site.register(Queue,QueueAdmin)
