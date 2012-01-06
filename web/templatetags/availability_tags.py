from django import template

register = template.Library()

@register.filter(name='get_full_score')
def get_full_score(availability):
	return availability.days * availability.sprint.one_day_score

@register.filter(name='get_remaining_score')
def get_remaining_score(availability):
	to_return = availability.days * availability.sprint.one_day_score
	for task in availability.user.task_set.filter(story__sprint=availability.sprint).all():
		to_return -= task.score
	return to_return
