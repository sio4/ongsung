from django.db import models

from django.dispatch import dispatcher
from django.db.models import signals

import uuid

# Create your models here.

class Host(models.Model):
	name = models.CharField(max_length=80)
	addr = models.IPAddressField(max_length=80)

	def __unicode__(self):
		return self.name



class Session(models.Model):
	time = models.DateTimeField(auto_now=True)
	uuid = models.CharField(max_length=36)
	host = models.ForeignKey(Host)
	context = models.CharField(max_length=80)

	def __unicode__(self):
		return str(self.uuid)

	def _set_uuid(self):
		self.uuid = str(uuid.uuid4())

	def link_to(self, host_addr):
		self._set_uuid()
		try:
			self.host = Host.objects.filter(addr=host_addr)[0]
		except:
			self.host = Host(name=host_addr,addr=host_addr)
			self.host.save()



PRIORITY_CHOICES = (
	('C', 'Critical'),
	('E', 'Error'),
	('W', 'Warning'),
	('N', 'Notice'),
	('L', 'Log'),
)

class Log(models.Model):
	"""
	session:	reference to session of connect
	statement:	log statement
	serial:		serial number. can be same if continued statement
	"""
	session = models.ForeignKey(Session, null=True)
	statement = models.CharField(max_length=256)
	serial = models.IntegerField(default=1)
	priority = models.CharField(max_length=1,
			choices=PRIORITY_CHOICES, default='L')
	time = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.time.strftime("%Y-%m-%d %H:%M:%S ") + self.priority + " " + self.statement


# strange
#def session_post_init(sender, instance, **kwargs):
#	instance._set_uuid()
#
#signals.post_init.connect(session_post_init, sender=Session)
