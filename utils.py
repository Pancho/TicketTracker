from django import forms
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.template.defaultfilters import slugify


class TTForm(forms.Form):
	def setup(self, request, last_post=None, initial=None):
		if initial:
			self.initial = initial


	def process(self, request):
		return


def init_form(request, form_action, form_class, last_post, initial=None):
	form_data = {"auto_id": '%s_%%s' % slugify(form_class.__name__.replace('Form', ''))}

	this_form_posted = last_post and last_post.get('form_class', '') == form_class.__name__

	if last_post and this_form_posted and last_post.get('error', False):
		form = form_class(last_post.get('post_data', {}), **form_data)
	else:
		form = form_class(**form_data)
		if this_form_posted:
			form.success = True

	if isinstance(form, TTForm):
		form.setup(request, last_post if this_form_posted else {}, initial)

	form.action = form_action
	return form


def process_form(request, form_class, home_name, params):
	if request.method == 'POST':
		form = form_class(request.POST, request.FILES)

		if isinstance(form, TTForm): # Setup the form, yet ignore the defaults, because they have no meaning here
			form.setup(request, None, None)

		error = False
		process_result = None

		if form.is_valid():
			if isinstance(form, TTForm):
				process_result = form.process(request)
			else:
				raise Exception("Tickettracker forms should implement TTForm or they should not be used here")
		else:
			error = True

		# Add form process results to session for redirect to work
		request.session['last_post'] = {'form_class': form_class.__name__, 'post_data': request.POST, 'result': process_result, 'error': error}

		if params:
			return HttpResponseRedirect(reverse(home_name, args=params.split('PARAM_SEPARATOR')))
		else:
			return HttpResponseRedirect(reverse(home_name))

	return HttpResponseNotAllowed(['POST'])


def init_formset(request, form_action, form_class, last_post, initial=None):
	form_data = {"auto_id": '%s_%%s' % slugify(form_class.__name__.replace('Form', ''))}
	
	this_form_posted = last_post and last_post.get('form_class', '') == form_class.__name__

	formset_factory_instance = formset_factory(form_class, can_delete=True)

	if last_post and this_form_posted and last_post.get('error', False):
		formset = formset_factory_instance(last_post.get('post_data', {}), **form_data)
		for form in formset:
			if isinstance(form, TTForm):
				form.setup(request, last_post if this_form_posted else {}, form.initial)
	else:
		formset = formset_factory_instance(initial=initial, **form_data)
		if this_form_posted:
			formset.success = True
		for form in formset:
			if isinstance(form, TTForm):
				form.setup(request, last_post if this_form_posted else {}, form.initial)


	formset.action = form_action
	return formset


def process_formset(request, form_class, home_name, params):
	if request.method == 'POST':
		formset_factory_instance = formset_factory(form_class, can_delete=True)
		formset = formset_factory_instance(request.POST, request.FILES)

		for form in formset:
			if isinstance(form, TTForm): # Setup the form, yet ignore the defaults, because they have no meaning here
				form.setup(request, None, None)

		error = False
		process_results = []
		
		for form in formset:
			if form.is_valid():
				if isinstance(form, TTForm):
					process_results.append(form.process(request))
				else:
					raise Exception("Tickettracker forms should implement TTForm or they should not be used here")
			else:
				error = True

		# Add form process results to session for redirect to work
		request.session['last_post'] = {'form_class': form_class.__name__, 'post_data': request.POST, 'result': process_results, 'error': error}

		if params:
			return HttpResponseRedirect(reverse(home_name, args=params.split('PARAM_SEPARATOR')))
		else:
			return HttpResponseRedirect(reverse(home_name))

	return HttpResponseNotAllowed(['POST'])


def get_session_data(request):
	if 'last_post' in request.session:
		data = request.session.get('last_post', None)
		del request.session['last_post']
		return data
	else:
		return None


def set_session_data(request, object):
	request.session['last_post'] = object
