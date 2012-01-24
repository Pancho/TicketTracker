from datetime import datetime, timedelta, date
# Making the following import future-proof
from time import strftime


try:
	import json
except:
	from django.utils import simplejson as json

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from web import forms, models
import utils


# Auth
def login(request):
	ctx = {'primary': 'login'}

	# Make sure user always lands where she wanted to
	request_method = request.method
	next_param = request.REQUEST.get('next', '')
	reason = request.REQUEST.get('reason', '')

	ctx['next'] = next_param
	ctx['reason'] = reason

	# Redirect to index if user is logged in or display login otherwise
	if request.user and request.user.is_authenticated():
		if request_method == 'GET':
			if next_param != '' and reason == '':
				return HttpResponseRedirect(next_param)
		else:
			if next_param != '' and  reason == '':
				return HttpResponseRedirect(next_param)
			elif next_param == '' and reason == '':
				return HttpResponseRedirect(reverse('web.index'))

	return auth_views.login(request, template_name='pages/login.html', authentication_form=forms.LoginForm, extra_context=ctx)


def password_reset_done(request):
	return render_to_response('pages/password_reset_done.html', {}, RequestContext(request))


# Index
@login_required
def index(request):
	return render_to_response('pages/index.html', {}, RequestContext(request))


# Board
@login_required
def board(request):
	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]
		board = current_sprint.board_set.all()[0]
		first_column_tag = board.boardcolumn_set.all().order_by('order')[0].tag
		board_columns = board.boardcolumn_set.all().order_by('order')
	else:
		current_sprint = None
		board = None
		first_column_tag = None
		board_columns = None
	ctx = {
		'sidebar_selected': 'board',
		'current_sprint': current_sprint,
		'board': board,
		'board_columns': board_columns,
		'first_column_tag': first_column_tag,
	}

	return render_to_response('pages/board.html', ctx, RequestContext(request))


@login_required
def board_story_next(request, id):
	try:
		story = models.Story.objects.get(id=id)
	except models.Story.DoesNotExist:
		raise Http404

	sprint = story.sprint
	board = sprint.board_set.all()[0]

	if story.state != 'DONE' and story.state != 'FIRE':
		current_column = board.boardcolumn_set.get(tag=story.state)
		next_column_tag = board.boardcolumn_set.get(order=current_column.order+1).tag
		if story.is_burning and next_column_tag == 'DONE':
			story.state = 'FIRE'
		else:
			story.state = next_column_tag
		story.save()

		# Move all the tasks too
		if story.state == 'DONE' or story.state == 'FIRE':
			for task in story.task_set.all():
				if task.state != 'TO_CLOSED':
					story_action = models.StoryAction()
					story_action.action = 'TO_CLOSED'
					story_action.task = task
					story_action.actor = request.user
					story_action.save()

					task.state = 'TO_CLOSED'
					task.save()



		action = models.BoardAction()
		action.story = story
		action.board_from = current_column.tag # Save previous state
		action.board_to = story.state # Save new state
		action.actor = request.user
		action.save()

	return HttpResponseRedirect(request.GET.get('return-to', reverse('web.board')))


@login_required
def board_story_previous(request, id):
	try:
		story = models.Story.objects.get(id=id)
	except models.Story.DoesNotExist:
		raise Http404

	sprint = story.sprint
	board = sprint.board_set.all()[0]
	first_column_tag = board.boardcolumn_set.all().order_by('order')[0].tag

	if story.state != first_column_tag:
		current_column = board.boardcolumn_set.get(tag=story.state)
		previous_column_tag = board.boardcolumn_set.get(order=current_column.order-1).tag

		if story.is_burning and previous_column_tag == 'DONE':
			story.state = board.boardcolumn_set.get(order=current_column.order-2).tag
		else:
			story.state = previous_column_tag

		story.save()

		action = models.BoardAction()
		action.story = story
		action.board_from = current_column.tag # Save previous state
		action.board_to = story.state # Save new state
		action.actor = request.user
		action.save()

	return HttpResponseRedirect(request.GET.get('return-to', reverse('web.board')))


@login_required
def board_story_move(request, id, to_column):
	if request.is_ajax():
		try:
			story = models.Story.objects.get(id=id)
		except models.Story.DoesNotExist:
			raise Http404

		previous_story_state = story.state

		story.state = to_column
		story.save()

		# Move all the tasks too
		if story.state == 'DONE' or story.state == 'FIRE':
			for task in story.task_set.all():
				if task.state != 'TO_CLOSED':
					story_action = models.StoryAction()
					story_action.action = 'TO_CLOSED'
					story_action.task = task
					story_action.actor = request.user
					story_action.save()

					task.state = 'TO_CLOSED'
					task.save()
		elif previous_story_state == 'DONE' or previous_story_state == 'FIRE':
			for task in story.task_set.all():
				if task.state == 'TO_CLOSED':
					story_action = models.StoryAction()
					if to_column == 'WAITING':
						story_action.action = 'TO_WAITING'
					else:
						story_action.action = 'TO_WORKING'
					story_action.task = task
					story_action.actor = request.user
					story_action.save()

					task.state = story_action.action
					task.save()


		action = models.BoardAction()
		action.story = story
		action.board_from = previous_story_state # Save previous state
		action.board_to = story.state # Save new state
		action.actor = request.user
		action.save()

		return HttpResponse('OK')
	else:
		raise Http404


#My Stuff
@login_required
def my_stuff(request):
	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]
		open_stories = list(models.Story.objects.filter(sprint=current_sprint).filter(task__owner=request.user).distinct())
		open_stories.sort(story_comparator)
	else:
		current_sprint = None
		open_stories = None



	ctx = {
		'sidebar_selected': 'mystuff',
		'current_sprint': current_sprint,
		'open_stories': open_stories,
	}

	return render_to_response('pages/my_stuff.html', ctx, RequestContext(request))


@login_required
def my_stuff_story_tasks(request, id):
	try:
		story = models.Story.objects.get(id=id)
	except models.Story.DoesNotExist:
		raise Http404

	open_stories = list(models.Story.objects.filter(sprint=story.sprint).filter(task__owner=request.user).distinct())
	open_stories.sort(story_comparator)

	ctx = {
		'sidebar_selected': 'mystuff',
		'selected_story': story,
		'current_sprint': story.sprint,
		'open_stories': open_stories,
	}

	return render_to_response('pages/my_stuff_story_tasks.html', ctx, RequestContext(request))


@login_required
def my_stuff_story_task_change_state(request, id, state):
	try:
		task = models.Task.objects.get(id=id)
	except models.Task.DoesNotExist:
		raise Http404

	state = 'TO_%s' % state.upper()

	story_action = models.StoryAction()
	story_action.action = state
	story_action.task = task
	story_action.actor = request.user
	story_action.save()

	task.state = state
	task.save()

	return HttpResponseRedirect(request.GET.get('return-to', reverse('web.index')))


@login_required
def my_stuff_story_fire(request, id=None):
	last_post = utils.get_session_data(request) or {}

	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]
		open_stories = list(models.Story.objects.filter(sprint=current_sprint).filter(task__owner=request.user).distinct())
		open_stories.sort(story_comparator)
	else:
		current_sprint = None
		open_stories = None

	initial = {
		'sprint_id': current_sprint.id if current_sprint else -1,
	}

	args = []

	if id:
		try:
			fire = models.Story.objects.get(id=id)
			initial.update({
				'id': fire.id,
			    'title': fire.title,
			    'story_description': fire.story_description,
			    'tags': fire.tags,
			    'score': fire.task_set.all()[0].score,
			    'owner': fire.task_set.all()[0].owner,
			})
		except models.Story.DoesNotExist:
			raise Http404

	ctx = {
		'form': utils.init_form(request, reverse('web.my_stuff_fire_submit', args=args), forms.FireForm, last_post, initial),
		'open_stories': open_stories,
		'current_sprint': current_sprint,
		'sidebar_selected': 'mystuff',
	}

	return render_to_response('pages/my_stuff_fire.html', ctx, RequestContext(request))


#Burndown Chart
@login_required
def burndown_chart(request):
	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]
		open_stories = list(models.Story.objects.filter(sprint=current_sprint).filter(task__owner=request.user).distinct())
		open_stories.sort(story_comparator)
	else:
		current_sprint = None
		open_stories = None

	ctx = {
		'sidebar_selected': 'bdchart',
		'current_sprint': current_sprint,
	}

	return render_to_response('pages/burndown_chart.html', ctx, RequestContext(request))


def burndown_chart_full_screen(request):
	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]
	else:
		current_sprint = None

	ctx = {
		'current_sprint': current_sprint,
	}

	return render_to_response('pages/burndown_chart_full_screen.html', ctx, RequestContext(request))


def burndown_chart_data(request, id=None):
	if not id:
		selected_sprint = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())[0]
		if not selected_sprint:
			raise Http404
	else:
		try:
			selected_sprint = models.Sprint.objects.get(id=id)
		except models.Sprint.DoesNotExist:
			raise Http404

	total_score = 0
	for story in selected_sprint.story_set.all():
		for task in story.task_set.all():
			total_score += task.score

	task_total_score = total_score
	fire_score = 0

	data = []

	day_count = (selected_sprint.date_ends - selected_sprint.date_begins).days + 1
	for single_date in [d for d in (selected_sprint.date_begins + timedelta(n) for n in range(day_count)) if d <= selected_sprint.date_ends]:
		if single_date < datetime.now():
			for action in models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)):
				if action.story.sprint == selected_sprint:
					story_score = 0
					for task in action.story.task_set.all():
						story_score += task.score
					if action.story.is_burning:
						if action.board_to == 'FIRE':
							fire_score += story_score
						if action.board_from == 'FIRE':
							fire_score -= story_score
					else:
						if action.board_to == 'DONE':
							total_score -= story_score
						if action.board_from == 'DONE':
							total_score += story_score
			for action in models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)):
				if action.task.story.sprint == selected_sprint and (action.task.story.is_burning == False or action.task.story.is_burning == None):
					if action.action == 'TO_CLOSED':
						task_total_score -= action.task.score
					if action.action == 'TO_WAITING' or action.action == 'TO_WORKING':
						task_total_score += action.task.score
			data.append([strftime("%m.%d.%Y", single_date.timetuple()), total_score, task_total_score, fire_score])
		else:
			data.append([strftime("%m.%d.%Y", single_date.timetuple()), None, None, None])
	
	return HttpResponse(json.dumps(data))


# Backlog
@login_required
def backlog(request, id = None, delete_selected=False, sprint=False):
	last_post = utils.get_session_data(request) or {}

	if delete_selected:
		ctx = {}
		if id:
			try:
				models.Story.objects.get(id=id).delete()
				return HttpResponseRedirect(reverse('web.backlog'))
			except models.Story.DoesNotExist:
				raise Http404
	else:
		open_stories = list(models.Story.objects.filter(state='BACKLOG'))
		open_stories.sort(story_comparator)
		ctx = {
			'sidebar_selected': 'backlog',
			'open_stories': open_stories
		}

		if id:
			try:
				if sprint:
					story = models.Story.objects.get(id=id)
					ctx['form'] = utils.init_form(request, reverse('web.backlog_story_storyparser_edit_submit_planning', args=[story.sprint.id]), forms.StoryParserForm, last_post, story)
				else:
					ctx['form'] = utils.init_form(request, reverse('web.backlog_story_storyparser_edit_submit', args=[id]), forms.StoryParserForm, last_post, models.Story.objects.get(id=id))
			except models.Story.DoesNotExist:
				raise Http404
		else:
			ctx['form'] = utils.init_form(request, reverse('web.backlog_story_submit', args=[]), forms.StoryParserForm, last_post, {})

	return render_to_response('pages/backlog.html', ctx, RequestContext(request))


def backlog_all_stories(request):
	open_stories = list(models.Story.objects.filter(state='BACKLOG'))
	open_stories.sort(story_comparator)
	ctx = {
		'stories': open_stories
	}

	return render_to_response('pages/backlog_all_stories.html', ctx, RequestContext(request))


@login_required
def backlog_tasks(request, story_id):
	last_post = utils.get_session_data(request) or {}

	story = None
	try:
		story = models.Story.objects.get(id=story_id)
	except models.Story.DoesNotExist:
		raise Http404

	open_stories = list(models.Story.objects.filter(state='BACKLOG'))
	open_stories.sort(story_comparator)

	ctx = {
		'story': story,
		'sidebar_selected': 'backlog',
		'open_stories': open_stories,
	    'task_formset': utils.init_formset(request, reverse('web.backlog_tasks_submit', args=[story_id]), forms.TaskForm, last_post, story.task_set.all().values())
	}

	return render_to_response('pages/tasks.html', ctx, RequestContext(request))


@login_required
def backlog_duplicate_story(request, story_id):
	try:
		story = models.Story.objects.get(id=story_id)
	except models.Story.DoesNotExist:
		raise Http404

	story_new = models.Story()
	story_new.title = story.title
	story_new.story_description = story.story_description
	story_new.moscow = story.moscow
	story_new.is_green = story.is_green
	story_new.tags = story.tags
	story_new.state = 'BACKLOG'
	story_new.time_boxed = story.time_boxed
	story_new.save()

	for task in story.task_set.all():
		task_new = models.Task()
		task_new.description = task.description
		task_new.score = task.score
		task_new.story = story_new
		task_new.owner = task.owner
		task_new.save()

	return HttpResponseRedirect(request.GET.get('return-to', reverse('web.index')))


# Sprint
@login_required
def sprint(request):
	days = []
	
	current_sprint_queryset = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())
	if current_sprint_queryset.count():
		current_sprint = current_sprint_queryset[0]

		day_count = (current_sprint.date_ends - current_sprint.date_begins).days + 1
		for single_date in [d for d in (current_sprint.date_begins + timedelta(n) for n in range(day_count)) if d <= current_sprint.date_ends]:
			if single_date < datetime.now():
				days.append({
					'formatted': strftime("%m.%d.%Y", single_date.timetuple()),
					'day': strftime("%d", single_date.timetuple()),
					'month': strftime("%m", single_date.timetuple()),
					'year': strftime("%Y", single_date.timetuple()),
					'board_actions_count': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'story_actions_count': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'fires_count': models.Story.objects.filter(sprint=current_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).distinct().count(),
				})
	else:
		current_sprint = None

	ctx = {
		'sidebar_selected': 'sprint',
		'days': days,
	}

	return render_to_response('pages/sprint.html', ctx, RequestContext(request))



def sprint_all_stories(request, id=None):
	if not id:
		selected_sprint = models.Sprint.objects.filter(date_begins__lt=datetime.now()).filter(date_ends__gt=datetime.now())[0]
		if not selected_sprint:
			raise Http404
	else:
		try:
			selected_sprint = models.Sprint.objects.get(id=id)
		except models.Sprint.DoesNotExist:
			raise Http404

	ctx = {
		'sprint': selected_sprint
	}

	return render_to_response('pages/sprint_list_stories.html', ctx, RequestContext(request))


@login_required
def sprint_day(request, day, month, year):
	current_sprint = models.Sprint.objects.filter(date_begins__lt=datetime.now()).order_by('-date_begins')[0]

	days = []
	day_data = {}

	day_count = (current_sprint.date_ends - current_sprint.date_begins).days + 1
	for single_date in [d for d in (current_sprint.date_begins + timedelta(n) for n in range(day_count)) if d <= current_sprint.date_ends]:
		if date(int(year), int(month), int(day)) == single_date.date():
			day_data = {
				'board_actions': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).order_by('-date'),
			    'story_actions': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).order_by('-date'),
			    'fires': models.Story.objects.filter(sprint=current_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).order_by('-created').distinct()
			}
		if single_date < datetime.now():
			days.append({
				'formatted': strftime("%m.%d.%Y", single_date.timetuple()),
				'day': strftime("%d", single_date.timetuple()),
				'month': strftime("%m", single_date.timetuple()),
				'year': strftime("%Y", single_date.timetuple()),
			    'board_actions_count': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
			    'story_actions_count': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
			    'fires_count': models.Story.objects.filter(sprint=current_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).distinct().count(),
			})

	ctx = {
		'selected_day': '%s.%s.%s' % (month, day, year),
		'sidebar_selected': 'sprint',
		'days': days,
		'day_data': day_data,
	}

	return render_to_response('pages/sprint_day.html', ctx, RequestContext(request))


@login_required
def sprint_overview(request, id, day=None, month=None, year=None):
	try:
		selected_sprint = models.Sprint.objects.get(id=id)
	except:
		raise Http404


	if day and month and year:
		days = []
		day_data = {}

		day_count = (selected_sprint.date_ends - selected_sprint.date_begins).days + 1
		for single_date in [d for d in (selected_sprint.date_begins + timedelta(n) for n in range(day_count)) if d <= selected_sprint.date_ends]:
			if date(int(year), int(month), int(day)) == single_date.date():
				day_data = {
					'board_actions': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).order_by('-date'),
					'story_actions': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).order_by('-date'),
					'fires': models.Story.objects.filter(sprint=selected_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).order_by('-created').distinct()
				}
			if single_date < datetime.now():
				days.append({
					'formatted': strftime("%m.%d.%Y", single_date.timetuple()),
					'day': strftime("%d", single_date.timetuple()),
					'month': strftime("%m", single_date.timetuple()),
					'year': strftime("%Y", single_date.timetuple()),
					'board_actions_count': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'story_actions_count': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'fires_count': models.Story.objects.filter(sprint=selected_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).distinct().count(),
				})

		ctx = {
			'selected_day': '%s.%s.%s' % (month, day, year),
			'selected_sprint': selected_sprint,
			'sidebar_selected': 'planning',
			'days': days,
			'day_data': day_data,
		}

		return render_to_response('pages/sprint_overview_day.html', ctx, RequestContext(request))
	else:
		days = []

		day_count = (selected_sprint.date_ends - selected_sprint.date_begins).days + 1
		for single_date in [d for d in (selected_sprint.date_begins + timedelta(n) for n in range(day_count)) if d <= selected_sprint.date_ends]:
			if single_date < datetime.now():
				days.append({
					'formatted': strftime("%m.%d.%Y", single_date.timetuple()),
					'day': strftime("%d", single_date.timetuple()),
					'month': strftime("%m", single_date.timetuple()),
					'year': strftime("%Y", single_date.timetuple()),
					'board_actions_count': models.BoardAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'story_actions_count': models.StoryAction.objects.filter(date__gt=single_date).filter(date__lt=single_date + timedelta(days=1)).count(),
					'fires_count': models.Story.objects.filter(sprint=selected_sprint).filter(is_burning=True).filter(created__gt=single_date).filter(created__lt=single_date + timedelta(days=1)).distinct().count(),
				})

		ctx = {
			'sidebar_selected': 'planning',
			'selected_sprint': selected_sprint,
		    'days': days,
		}

		return render_to_response('pages/sprint_overview.html', ctx, RequestContext(request))




# Planning
@login_required
def planning(request):
	ctx = {
		'sidebar_selected': 'planning',
	    'sprints': models.Sprint.objects.order_by('-sprint_number')
	}
	return render_to_response('pages/planning.html', ctx, RequestContext(request))


def planning_new_sprint(request):
	last_post = utils.get_session_data(request) or {}

	ctx = {
		'sidebar_selected': 'planning',
	    'form': utils.init_form(request, reverse('web.planning_new_sprint_submit', args=[]), forms.SprintForm, last_post, {})
	}
	return render_to_response('pages/planning_new_sprint.html', ctx, RequestContext(request))


@login_required
def planning_sprint_availability(request, id):
	last_post = utils.get_session_data(request) or {}

	try:
		sprint = models.Sprint.objects.get(id=id)
	except models.Sprint.DoesNotExist:
		raise Http404

	ctx = {
		'sidebar_selected': 'planning',
		'sprint': sprint,
	    'availability_formset': utils.init_formset(request, reverse('web.planning_sprint_availability_submit', args=[sprint.id]), forms.AvailabilityForm, last_post, sprint.availability_set.all().values())
	}

	return render_to_response('pages/planning_sprint_availability.html', ctx, RequestContext(request))


@login_required
def planning_sprint_stories(request, id, from_backlog=None, to_backlog=None):
	try:
		sprint = models.Sprint.objects.get(id=id)
		first_board_column = sprint.board_set.all()[0].boardcolumn_set.all().order_by('order')[0].tag
	except models.Sprint.DoesNotExist:
		raise Http404

	if from_backlog:
		try:
			story = models.Story.objects.get(id=from_backlog)
			story.sprint = sprint
			story.state = first_board_column
			story.save()
		except models.Story.DoesNotExist:
			raise Http404

	if to_backlog:
		try:
			story = models.Story.objects.get(id=to_backlog)
			story.sprint = None
			story.state = 'BACKLOG'
			story.save()
		except models.Story.DoesNotExist:
			raise Http404

	open_stories = list(models.Story.objects.filter(state='BACKLOG'))
	sprint_stories = list(sprint.story_set.all())
	sprint_stories.sort(story_comparator)
	open_stories.sort(story_comparator)

	ctx = {
		'sidebar_selected': 'planning',
		'sprint': sprint,
		'sprint_stories': sprint_stories,
	    'backlog': open_stories,
	}

	return render_to_response('pages/planning_sprint_stories.html', ctx, RequestContext(request))


@login_required
def planning_sprint_stories_owner(request, id, story_id):
	last_post = utils.get_session_data(request) or {}

	try:
		sprint = models.Sprint.objects.get(id=id)
	except models.Sprint.DoesNotExist:
		raise Http404

	try:
		story = models.Story.objects.get(id=story_id)
	except models.Sprint.DoesNotExist:
		raise Http404

	ctx = {
		'sidebar_selected': 'planning',
		'sprint': sprint,
	    'story': story,
	    'availabilities': sprint.availability_set.all(),
	    'task_owner_formset': utils.init_formset(request, reverse('web.planning_sprint_stories_owner_submit', args=['%sPARAM_SEPARATOR%s' % (sprint.id, story.id)]), forms.TaskOwnerForm, last_post, story.task_set.all().values()),
	}

	return render_to_response('pages/planning_sprint_stories_availability.html', ctx, RequestContext(request))


def tabbed_view(request, id):
	ctx = {
		'sprint': models.Sprint.objects.get(id=id)
	}

	return render_to_response('pages/tabbed_view.html', ctx, RequestContext(request))


# FORM HANDLING
@login_required
def process_form(request, form_class, home_name, params=''):
	return utils.process_form(request, form_class, home_name, params)


@login_required
def process_formset(request, form_class, home_name, params=''):
	return utils.process_formset(request, form_class, home_name, params)


# COMPARATOR
MOSCOW_PRIORITY_MAP = {
	'M': 1,
	'S': 2,
	'C': 3,
	'W': 4,
	'': 5,
}


def story_comparator(x, y):
	return cmp(MOSCOW_PRIORITY_MAP[x.moscow], MOSCOW_PRIORITY_MAP[y.moscow])