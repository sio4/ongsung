from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Protocol(models.Model):
	name = models.CharField(max_length=80)
	port = models.IntegerField()
	handler = models.CharField(max_length=128,null=True)

	def __unicode__(self):
		return self.name + "(" + str(self.port) + ")"

class Device(models.Model):
	name = models.CharField(max_length=80)
	addr = models.IPAddressField(max_length=80)
	port = models.IntegerField(null=True)
	prot = models.ForeignKey(Protocol)

	def __unicode__(self):
		return self.name + "(" + str(self.addr) + ")"

class Bookmark(models.Model):
	user = models.ForeignKey(User)
	device = models.ForeignKey(Device)
	stared = models.BooleanField(default=False)
	last_date = models.DateTimeField('last used')
	count = models.IntegerField(default=1)

	def __unicode__(self):
		return self.user.__unicode__() + "@" + self.device.name

