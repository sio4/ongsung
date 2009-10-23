from django import template

from blog.models import Roll,Page

register = template.Library()


@register.inclusion_tag('blog/rollbox.html')
def rollbox():
	top10 = Roll.objects.filter(rank__gt=0).order_by('-rank')[0:9]
	rolls = Roll.objects.all().order_by('title')
	return {'top10':top10, 'rolls':rolls}

@register.inclusion_tag('blog/stickies.html')
def stickies():
	stickies = Page.objects.filter(sticky=True,published=True,private=False)
	return {'pages':stickies}
