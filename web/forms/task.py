from django import forms
from django.contrib.auth.models import User
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

class TaskForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	description = forms.CharField(max_length=1024, label='Task Description', required=True, widget=forms.Textarea())
	score = forms.IntegerField(label='Task Score', widget=forms.Select(choices=POKER_SCORES, attrs={'class': 'tt-inline-select'}))

	def process(self, request):
		task, created = models.Task.objects.get_or_create(id=self.cleaned_data['id'], story=models.Story.objects.get(id=request.POST.get('story_id', -1)))
		if self.cleaned_data.get('DELETE', False):
			task.delete()
		else:
			task.state = 'TO_WAITING'
			task.description = self.cleaned_data['description']
			task.score = self.cleaned_data['score']
			task.save()

		return {
			'completed': True,
		    'task': task,
		}


class TaskOwnerForm(TaskForm):
	owner = forms.ChoiceField(label='Employee')


	def setup(self, request, last_post=None, initial=None):
		choices = []
		for user in User.objects.filter(profile__company=request.user.get_profile().company).order_by('first_name').all():
			choices.append((user.id, '%s %s' % (user.first_name, user.last_name)))
		self.fields['owner'].choices = choices
		if initial:
			self.fields['owner'].initial = initial.get('owner_id', -1)


	def process(self, request):
		task, created = models.Task.objects.get_or_create(id=self.cleaned_data['id'], story=models.Story.objects.get(id=request.POST.get('story_id', -1)))
		if self.cleaned_data.get('DELETE', False):
			task.delete()
		else:
			task.description = self.cleaned_data['description']
			task.score = self.cleaned_data['score']
			task.owner = User.objects.get(id=self.cleaned_data['owner'])
			task.save()

		return {
			'completed': True,
		    'task': task,
		}