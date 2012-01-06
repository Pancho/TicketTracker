from django import forms


import utils
from web import models


class SprintForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	date_begins = forms.DateTimeField(label='Start Date', widget=forms.TextInput(attrs={'class': 'tt-date-field'}))
	date_ends = forms.DateTimeField(label='Finish Date', widget=forms.TextInput(attrs={'class': 'tt-date-field'}))
	sprint_number = forms.IntegerField(label='Sprint Number')
	name = forms.CharField(max_length=256, label='Sprint Name')
	goals = forms.CharField(max_length=10000, widget=forms.Textarea())
	one_day_score = forms.IntegerField()
	board = forms.ChoiceField(label='Board Type')


	def setup(self, request, last_post=None, initial=None):
		choices = []
		for board_prototype in models.BoardPrototype.objects.all():
			choices.append((board_prototype.id, board_prototype.readable_description))
		self.fields['board'].choices = choices
		if initial:
			self.fields['board'].initial = initial.get('board_id', -1)

	
	def process(self, request):
		try:
			sprint = models.Sprint.objects.get(id=self.cleaned_data['id'])
		except models.Sprint.DoesNotExist:
			sprint = models.Sprint()

		sprint.date_begins = self.cleaned_data['date_begins']
		sprint.date_ends = self.cleaned_data['date_ends']
		sprint.sprint_number = self.cleaned_data['sprint_number']
		sprint.name = self.cleaned_data['name']
		sprint.goals = self.cleaned_data['goals']
		sprint.one_day_score = self.cleaned_data['one_day_score']
		sprint.save()

		# give this sprint new board if it has none or has a different one than the one that was selected in the form
		if len(sprint.board_set.all()) == 0 or sprint.board_set.all()[0].from_prototype.id != self.cleaned_data['board']:
			models.BoardPrototype.objects.get(id=self.cleaned_data['board']).construct_board(sprint)
		
		return {
			'completed': True,
		    'sprint': sprint,
		}
