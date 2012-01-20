from django import forms
from django.contrib.auth.models import User
from storyparser.converter import Converter

import utils
from web import models

POKER_SCORES = [
	(0, '0'),
	(1, '1'),
	(2, '2'),
	(3, '3'),
	(5, '5'),
	(8, '8'),
	(13, '13'),
	(20, '20'),
	(40, '40'),
	(100, '100'),
	(-1, 'Infinity'),
	(-2, '?'),
]

class StoryForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	title = forms.CharField(max_length=128, label='Story Title')
	story_description = forms.CharField(max_length=2048, label='User Story', widget=forms.Textarea())
	tasks = forms.CharField(max_length=2048, label='Story Tasks', widget=forms.Textarea(), help_text='Example for each line: "-  Task Description (5). you cannot use "(" and ")" characters here!"', required=False)
	moscow = forms.ChoiceField(choices=models.MOSCOW)
	is_green = forms.BooleanField(label='Is Story Green?', widget=forms.CheckboxInput(attrs={'class':'tt-checkbox'}), required=False)
	time_boxed = forms.BooleanField(label='Is Score Timeboxed?', widget=forms.CheckboxInput(attrs={'class':'tt-checkbox'}), required=False)
	tags = forms.CharField(max_length=128, label='Story Tags', required=False)


	def setup(self, request, last_post=None, initial=None):
		if initial:
			self.fields['id'].initial = initial.get('id', None)
			self.fields['title'].initial = initial.get('title', '')
			self.fields['story_description'].initial = initial.get('story_description', '')
			self.fields['moscow'].initial = initial.get('moscow', 'W')
			self.fields['is_green'].initial = initial.get('is_green', False)
			self.fields['time_boxed'].initial = initial.get('time_boxed', False)
			self.fields['tags'].initial = initial.get('tags', '')
			if initial.get('id', None):
				task_strings = []
				for task in models.Story.objects.get(id=initial.get('id')).task_set.all():
					task_strings.append('- %s (%d)' % (task.description, task.score))
				self.fields['tasks'].initial = '\n'.join(task_strings)

	def process(self, request):
		story, created = models.Story.objects.get_or_create(id=self.cleaned_data['id'])
		story.title = self.cleaned_data['title']
		story.story_description = self.cleaned_data['story_description']
		story.moscow = self.cleaned_data['moscow']
		story.is_green = self.cleaned_data['is_green']
		story.time_boxed = self.cleaned_data['time_boxed']
		story.tags = self.cleaned_data['tags']
		story.state = 'BACKLOG'
		story.created_by = request.user
		story.save()
		construct_tasks(self.cleaned_data['tasks'], story)
		return {
			'completed': True,
		    'story': story,
		}


class StoryParserForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	story = forms.CharField(label='User Story', widget=forms.Textarea({'cols': 100, 'rows': 20, 'class': 'tt-story-textarea'}))


	def setup(self, request, last_post=None, initial=None):
		if initial:
			self.fields['id'].initial = initial.id
			self.fields['story'].initial = Converter.django_story_to_text(initial, initial.task_set.all())

	def process(self, request):
		story, tasks = Converter.text_to_django_story(self.cleaned_data['story'].replace(r'\r\n', r'\n'))
		if self.cleaned_data['id'] and self.cleaned_data['id'] != '':
			existing_story = models.Story.objects.get(id=self.cleaned_data['id'])
			story.id = existing_story.id
			story.sprint = existing_story.sprint
			story.created_by = request.user
		else:
			story.state = 'BACKLOG'
			story.created_by = request.user
		story.save()

		for task in story.task_set.all():
			task.delete()

		for task in tasks:
			task.story = story
			task.save()

		return {
			'story': story
		}


class FireForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	sprint_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	title = forms.CharField(max_length=128, label='Story Title')
	story_description = forms.CharField(max_length=2048, label='User Story', widget=forms.Textarea())
	tags = forms.CharField(max_length=128, label='Story Tags', required=False)
	score = forms.IntegerField(label='Task Score', widget=forms.Select(choices=POKER_SCORES, attrs={'class': 'tt-inline-select'}))
	owner = forms.ChoiceField(label='Employee')


	class Meta:
		exclude = ('tasks',)


	def setup(self, request, last_post=None, initial=None):
		choices = []
		for user in User.objects.filter(profile__company=request.user.get_profile().company).all():
			choices.append((user.id, '%s %s' % (user.first_name, user.last_name)))
		self.fields['owner'].choices = choices
		if initial:
			self.fields['id'].initial = initial.get('id', None)
			self.fields['sprint_id'].initial = initial.get('sprint_id', -1)
			self.fields['title'].initial = initial.get('title', '')
			self.fields['story_description'].initial = initial.get('story_description', '')
			self.fields['tags'].initial = initial.get('tags', '')
			self.fields['score'].initial = initial.get('score', 0)
			self.fields['owner'].initial = initial.get('owner_id', -1)


	def process(self, request):
		owner = User.objects.get(id=self.cleaned_data['owner'])
		if self.cleaned_data['sprint_id'] > 0:
			sprint = models.Sprint.objects.get(id=self.cleaned_data['sprint_id'])
		else:
			sprint = None

		story, created = models.Story.objects.get_or_create(id=self.cleaned_data['id'])
		story.title = self.cleaned_data['title']
		story.story_description = self.cleaned_data['story_description']
		story.moscow = 'M'
		story.is_green = False
		story.time_boxed = False
		story.is_burning = True
		if not sprint:
			story.state = 'BACKLOG'
		else:
			story.sprint = sprint
			story.state = 'WAITING'
		story.tags = self.cleaned_data['tags']
		story.created_by = request.user
		story.save()

		if len(story.task_set.all()):
			fire_task = story.task_set.all()[0]
			fire_task.score = self.cleaned_data['score']
			fire_task.owner = owner
		else:
			fire_task = models.Task(description='Complete', score=self.cleaned_data['score'], state="TO_WAITING", owner=owner, story=story)
		fire_task.save()
		
		return {
			'completed': True,
		    'story': story,
		    'fire_task': fire_task,
		}


def construct_tasks(text, story):
	# Clean task set
	story.task_set.all().delete()
	# Create task set
	for line in text.split('\n'):
		stripped_line = line.replace('-', '').strip()
		task_description = stripped_line[0:stripped_line.find('(')].strip()
		task_score = stripped_line[stripped_line.find('(') + 1:stripped_line.find(')')]

		task_exists = story.task_set.filter(description=task_description, score=task_score).count() == 1

		if not task_exists:
			task = models.Task()
			task.story = story
			task.description = task_description
			task.score = task_score
			task.state = 'TO_WAITING'
			task.save()
