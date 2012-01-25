from datetime import datetime


from django import template

register = template.Library()

@register.filter(name='calculate_sprint_score')
def calculate_score(sprint):
	to_return = 0
	for story in sprint.story_set.all():
		for ticket in story.task_set.filter():
			if ticket.score:
				to_return += ticket.score
	return to_return

@register.filter(name='calculate_available_sprint_score')
def calculate_available_sprint_score(sprint):
	to_return = 0
	for availability in sprint.availability_set.all():
		to_return += availability.days * sprint.one_day_score
	return to_return

@register.filter(name='is_finished')
def is_finished(sprint):
	return sprint.date_ends < datetime.now()

@register.filter(name='is_in_progress')
def is_in_progress(sprint):
	return sprint.date_begins < datetime.now() and sprint.date_ends > datetime.now()

@register.filter(name='is_in_future')
def is_in_future(sprint):
	return sprint.date_begins > datetime.now()