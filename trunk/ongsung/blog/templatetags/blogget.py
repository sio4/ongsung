from django import template

from blog.models import Roll,Page

register = template.Library()


@register.inclusion_tag('blog/rollbox.html')
def rollbox():
	rolls = Roll.objects.all().order_by('rank')
	return {'rolls':rolls}

@register.inclusion_tag('blog/stickies.html')
def stickies():
	stickies = Page.objects.filter(sticky=True,published=True,private=False)
	return {'pages':stickies}
