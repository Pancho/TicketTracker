from django import template

register = template.Library()

@register.filter(name='humanize')
def humanize(value):
	if value.action == 'TO_WORKING':
		return "working"
	if value.action == 'TO_CLOSED':
		return "closed"
	if value.action == 'TO_WAITING':
		return "waiting"
