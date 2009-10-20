from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Page(models.Model):
	subject = models.CharField(max_length=80)
	content = models.TextField()
	author = models.ForeignKey(User)
	category = models.ForeignKey('Category', null=True)

	sticky = models.BooleanField(default=False)
	published = models.BooleanField(default=False)
	private = models.BooleanField(default=False)

	posted_at = models.DateTimeField('posted at', auto_now=True)
	edited_at = models.DateTimeField('edited at', auto_now=True)

	def __unicode__(self):
		return self.subject

	def tags(self):
		tags = Tag.objects.filter(page=self)
		return tags

	def comments(self):
		comments = Comment.objects.filter(page=self)
		return comments


class Tag(models.Model):
	name = models.CharField(max_length=80)
	page = models.ForeignKey(Page)

	def __unicode__(self):
		return self.name


class Comment(models.Model):
	page = models.ForeignKey(Page)
	author = models.ForeignKey(User)
	comment = models.TextField()

	posted_at = models.DateTimeField('posted at', auto_now=True)

	def __unicode__(self):
		return self.comment


class Category(models.Model):
	name = models.CharField(max_length=30)

	def __unicode__(self):
		return self.name

	def pages(self):
		pages = Page.objects.filter(category=self)
		return pages


class Roll(models.Model):
	title = models.CharField(max_length=30)
	link = models.URLField(verify_exists=False)
	rank = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title

