from django import template

from blog.models import Roll

register = template.Library()


@register.inclusion_tag('blog/rollbox.html')
def rollbox():
	rolls = Roll.objects.all()
	return {'rolls':rolls}
