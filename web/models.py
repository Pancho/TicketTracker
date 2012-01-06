# Making the following import future-proof
try:
	import json
except:
	from django.utils import simplejson as json


from django.contrib.auth.models import User
from django.db import models


MOSCOW = [
	('M', 'Must'),
	('S', 'Should'),
	('C', 'Could'),
	('W', 'Would'),
]


class Profile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	company = models.CharField(max_length=1024)

	def __unicode__(self):
		return u'%s profile' % self.user


class Sprint(models.Model):
	date_begins = models.DateTimeField()
	date_ends = models.DateTimeField()
	sprint_number = models.IntegerField()
	name = models.CharField(max_length=256)
	goals = models.TextField()
	one_day_score = models.IntegerField()


class Availability(models.Model):
	user = models.ForeignKey(to=User)
	sprint = models.ForeignKey(to=Sprint)
	days = models.IntegerField(null=True, blank=True)


class Story(models.Model):
	title = models.CharField(max_length=256)
	story_description = models.TextField()
	created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	created_by = models.ForeignKey(to=User, null=True, blank=True)
	miss_planned = models.NullBooleanField(default=False)
	additional_notes = models.TextField()
	moscow = models.CharField(max_length=10, choices=MOSCOW)
	is_green = models.NullBooleanField(default=False)
	is_burning = models.NullBooleanField(default=False)
	sprint = models.ForeignKey(to=Sprint, null=True, blank=True)
	tags = models.CharField(max_length=1024, null=True, blank=True)
	state = models.CharField(max_length=128, null=True, blank=True)
	time_boxed = models.NullBooleanField(default=False)


class Task(models.Model):
	description = models.CharField(max_length=1024)
	score = models.IntegerField(null=True, blank=True)
	story = models.ForeignKey(to=Story, null=False, blank=False)
	state = models.CharField(max_length=128, null=True, blank=True)
	owner = models.ForeignKey(to=User, null=True, blank=True)


class BoardPrototype(models.Model):
	columns_json = models.TextField()
	readable_description = models.TextField()


	def construct_board(self, sprint):
		board = Board()
		board.sprint = sprint
		board.from_prototype = self
		board.save()

		object = json.loads(self.columns_json)
		for key, value in object.iteritems():
			column = BoardColumn()
			column.title = key
			column.tag = value.get('tag', '')
			column.order = value.get('order', '')
			column.board = board
			column.save()


class Board(models.Model):
	sprint = models.ForeignKey(to=Sprint, null=True, blank=True)
	from_prototype = models.ForeignKey(to=BoardPrototype)


class BoardColumn(models.Model):
	title = models.CharField(max_length=256)
	tag = models.CharField(max_length=256)
	board = models.ForeignKey(to=Board)
	order = models.IntegerField()


	def get_stories(self):
		return self.board.sprint.story_set.filter(state=self.tag)


class BoardAction(models.Model):
	story = models.ForeignKey(to=Story)
	date = models.DateTimeField(auto_now_add=True)
	board_from = models.CharField(max_length=128)
	board_to = models.CharField(max_length=128)
	actor = models.ForeignKey(to=User)


class StoryAction(models.Model):
	task = models.ForeignKey(to=Task)
	date = models.DateTimeField(auto_now_add=True)
	action = models.CharField(max_length=128)
	actor = models.ForeignKey(to=User)


class Log(models.Model):
	type = models.CharField(max_length=1024)
	component = models.CharField(max_length=1024)
	ip = models.CharField(max_length=1024)
	comment = models.TextField()
	pickled_data = models.TextField()
	request_data = models.TextField()
	date_created = models.DateTimeField(auto_now=True)