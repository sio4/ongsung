from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.

class Feature(models.Model):
	name = models.CharField(max_length=80)
	description = models.TextField(null=True)

	def __unicode__(self):
		return self.name

class Worker(models.Model):
	name = models.CharField(max_length=80)
	addr = models.IPAddressField(max_length=80)
	features = models.ManyToManyField(Feature)

	def __unicode__(self):
		return self.name + " (" + self.addr + ")"

	def point(self):
		point = 0
		for q in self.queue_set.all():
			point += q.running_time().seconds / 60
			# one minute = one point
		return point

	def current_jobs(self):
		list = []
		for q in self.queue_set.all().order_by('-id'):
			if q.status == 'R':
				list.append(q)
		return list


STATUS_CHOICES = (
	('N', 'New'),
	('T', 'Taken'),
	('R', 'Running'),
	('D', 'Done'),
	('E', 'Error'),
	('C', 'Dropped'),
)

class Queue(models.Model):
	owner = models.ForeignKey(User)
	command = models.CharField(max_length=128)
	feature = models.ForeignKey(Feature)
	worker = models.ForeignKey(Worker, null=True)
	info = models.CharField(max_length=128, null=True)

	status = models.CharField(max_length=1,
			choices=STATUS_CHOICES, default='N')
	created_at = models.DateTimeField('created time', auto_now_add=True)
	updated_at = models.DateTimeField('updated time', auto_now=True)
	started_at = models.DateTimeField('taken at', null=True)
	finished_at = models.DateTimeField('finished at', null=True)
	description = models.TextField(null=True)

	def __unicode__(self):
		return '"' + self.command + '" for ' + self.owner.__unicode__()

	def running_time(self):
		if self.status == 'D':
			return self.finished_at - self.started_at
		elif self.status == 'R':
			return datetime.datetime.now() - self.started_at
		return 0

	def waiting_time(self):
		if self.started_at:
			return self.started_at - self.created_at
		else:
			return datetime.datetime.now() - self.created_at

