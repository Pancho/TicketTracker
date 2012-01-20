from django import template

register = template.Library()

@register.filter(name='calculate_score')
def calculate_score(story):
	to_return = 0
	for task in story.task_set.all():
		if task.score:
			to_return += task.score
	return to_return


@register.filter(name='calculate_score_humanize')
def calculate_score_humanize(story):
	to_return = 0
	task_count = story.task_set.all().count()
	planned = 0
	for task in story.task_set.all():
		if task.owner is not None:
			planned += 1
		if task.score:
			to_return += task.score
	if not planned:
		return '%d, not planned' % to_return
	elif planned < task_count:
		return '%d, not fully planned' % to_return
	elif planned == task_count:
		return '%d, fully planned' % to_return
