from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='print_classes')
def print_classes(value):
	classes = []
	if len(value.errors):
		classes.append('error')
	if 'class' in value.field.widget.attrs:
		classes.append(value.field.widget.attrs['class'])
	if len(classes):
		return mark_safe(' class="%s"' % " ".join(classes))
	else:
		return ''

@register.filter(name='one_line')
def one_line(value):
	return mark_safe(value.__unicode__().replace('>\n<', '><'))
