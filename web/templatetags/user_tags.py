from django import template

register = template.Library()

@register.filter(name='name_initial')
def name_initial(value):
	if len(value):
		return value[0]
	else:
		return ''
