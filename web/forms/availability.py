from django import forms
from django.contrib.auth.models import User
import utils
from web import models


class AvailabilityForm(utils.TTForm):
	id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	user = forms.ChoiceField(label='Employee')
	days = forms.IntegerField(label='Days Available')


	def setup(self, request, last_post=None, initial=None):
		choices = []
		for user in User.objects.filter(profile__company=request.user.get_profile().company).order_by('first_name').all():
			choices.append((user.id, '%s %s' % (user.first_name, user.last_name)))
		self.fields['user'].choices = choices
		if initial:
			self.fields['user'].initial = initial.get('user_id', -1)


	def process(self, request):
		try:
			availability = models.Availability.objects.get(id=self.cleaned_data['id'])
		except models.Availability.DoesNotExist:
			availability = models.Availability()

		if self.cleaned_data['DELETE']:
			availability.delete()
		else:
			availability.user = User.objects.get(id=self.cleaned_data['user'])
			availability.sprint = models.Sprint.objects.get(id=request.POST.get('sprint_id', -1))
			availability.days = self.cleaned_data['days']
			availability.save()

		return {
			'completed': True,
		    'availability': availability,
		}