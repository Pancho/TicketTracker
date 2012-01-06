from django import template
from web import models


register = template.Library()


@register.filter(name='pretty_print_column_name_from')
def pretty_print_column_name_from(value):
	return models.BoardColumn.objects.get(board__sprint=value.story.sprint,tag=value.board_to).title

@register.filter(name='pretty_print_column_name_to')
def pretty_print_column_name_to(value):
	return models.BoardColumn.objects.get(board__sprint=value.story.sprint,tag=value.board_from).title
