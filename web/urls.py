from django.conf.urls.defaults import *
from web import forms


urlpatterns = patterns('web.views',

	# Credentials
	url(r'^login$', 'login', name='web.login'),

	# Index
    url(r'^$', 'index', name='web.index'),

    # Board
    url(r'^board/$', 'board', name='web.board'),
    url(r'^board/story/(?P<id>\d+)/next$', 'board_story_next', name='web.board_story_next'),
    url(r'^board/story/(?P<id>\d+)/previous$', 'board_story_previous', name='web.board_story_previous'),
    url(r'^board/story/move/(?P<id>\d+)/(?P<to_column>[-\w]+)/$', 'board_story_move', name='web.board_story_move'),

	# My Stuff
	url(r'^my-stuff/$', 'my_stuff', name='web.my_stuff'),
	url(r'^my-stuff/story/(?P<id>\d+)/tasks/$', 'my_stuff_story_tasks', name='web.my_stuff_story_tasks'),
	url(r'^my-stuff/story/task/(?P<id>\d+)/state/to/(?P<state>\w+)/$', 'my_stuff_story_task_change_state', name='web.my_stuff_story_task_change_state'),
	url(r'^my-stuff/story/fire/$', 'my_stuff_story_fire', name='web.my_stuff_story_fire'),
	url(r'^my-stuff/story/fire/(?P<id>\d+)/$', 'my_stuff_story_fire', name='web.my_stuff_story_fire_edit'),

	# My Stuff Forms
	url(r'^my-stuff/fire/submit/$', 'process_form', {'form_class': forms.FireForm, 'home_name': 'web.my_stuff'}, name='web.my_stuff_fire_submit'),
	url(r'^my-stuff/fire/submit/edit/(?P<params>\w+)/$', 'process_form', {'form_class': forms.FireForm, 'home_name': 'web.my_stuff'}, name='web.my_stuff_fire_submit_edit'),

    # Burndown Chart
    url(r'^burndown-chart/$', 'burndown_chart', name='web.burndown_chart'),
    url(r'^burndown-chart-full-screen/$', 'burndown_chart_full_screen', name='web.burndown_chart_full_screen'),
    url(r'^burndown-chart/data/$', 'burndown_chart_data', name='web.burndown_chart_data'),
    url(r'^burndown-chart/data/sprint/(?P<id>\d+)/$', 'burndown_chart_data', name='web.burndown_chart_data_sprint'),

    # Backlog
	url(r'^backlog/$', 'backlog', name='web.backlog'),
	url(r'^backlog/all-stories/$', 'backlog_all_stories', name='web.backlog_all_stories'),
	url(r'^backlog/story/edit/(?P<id>\d+)/$', 'backlog', name='web.backlog_story_edit'),
	url(r'^backlog/story/edit/(?P<id>\d+)/story_parser/$', 'backlog', name='web.backlog_story_storyparser_edit'),
	url(r'^backlog/story/edit/(?P<id>\d+)/story_parser/planning/$', 'backlog', {'sprint': True}, name='web.backlog_story_storyparser_edit_planning'),
	url(r'^backlog/story/delete/(?P<id>\d+)/$', 'backlog', {'delete_selected': True}, name='web.backlog_story_delete'),
	url(r'^backlog/story/(?P<story_id>\d+)/tasks/$', 'backlog_tasks', name='web.backlog_tasks'),
	url(r'^backlog/story/(?P<story_id>\d+)/copy/$', 'backlog_duplicate_story', name='web.backlog_duplicate_story'),
    # Backlog Forms
    url(r'^backlog/story/submit/$', 'process_form', {'form_class': forms.StoryParserForm, 'home_name': 'web.backlog'}, name='web.backlog_story_submit'),
    url(r'^backlog/story/submit/edit/(?P<params>\w+)/$', 'process_form', {'form_class': forms.StoryForm, 'home_name': 'web.backlog_tasks'}, name='web.backlog_story_edit_submit'),
    url(r'^backlog/story/submit/storyparser/$', 'process_form', {'form_class': forms.StoryParserForm, 'home_name': 'web.backlog'}, name='web.backlog_story_storyparser_submit'),
    url(r'^backlog/story/submit/edit/(?P<params>\w+)/storyparser/$', 'process_form', {'form_class': forms.StoryParserForm, 'home_name': 'web.backlog_story_storyparser_edit'}, name='web.backlog_story_storyparser_edit_submit'),
    url(r'^backlog/story/submit/edit/(?P<params>\w+)/storyparser/planning/$', 'process_form', {'form_class': forms.StoryParserForm, 'home_name': 'web.planning_sprint_stories'}, name='web.backlog_story_storyparser_edit_submit_planning'),
    url(r'^backlog/story/tasks/edit/(?P<params>\w+)/$', 'process_formset', {'form_class': forms.TaskForm, 'home_name': 'web.backlog_tasks'}, name='web.backlog_tasks_submit'),

	# Sprint
	url(r'^sprint/$', 'sprint', name='web.sprint'),
	url(r'^sprint/all-stories/$', 'sprint_all_stories', name='web.sprint_all_stories'),
	url(r'^sprint/(?P<id>\d+)/all-stories/$', 'sprint_all_stories', name='web.sprint_all_stories_sprint'),
	url(r'^sprint/day/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', 'sprint_day', name='web.sprint_day'),
	url(r'^sprint/(?P<id>\d+)/overview/$', 'sprint_overview', name='web.sprint_overview'),
	url(r'^sprint/(?P<id>\d+)/overview/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', 'sprint_overview', name='web.sprint_overview_day'),

    # Planning
    url(r'^planning/$', 'planning', name='web.planning'),
    url(r'^planning/sprint/new/$', 'planning_new_sprint', name='web.planning_new_sprint'),
    url(r'^planning/sprint/(?P<id>\d+)/availability/$', 'planning_sprint_availability', name='web.planning_sprint_availability'),
    url(r'^planning/sprint/(?P<id>\d+)/stories/$', 'planning_sprint_stories', name='web.planning_sprint_stories'),
    url(r'^planning/sprint/(?P<id>\d+)/stories/add/(?P<from_backlog>\d+)/$', 'planning_sprint_stories', name='web.planning_sprint_stories_add'),
    url(r'^planning/sprint/(?P<id>\d+)/stories/remove/(?P<to_backlog>\d+)/$', 'planning_sprint_stories', name='web.planning_sprint_stories_remove'),
    url(r'^planning/sprint/(?P<id>\d+)/stories/owner/(?P<story_id>\d+)/$', 'planning_sprint_stories_owner', name='web.planning_sprint_stories_owner'),
    # Planning Forms
    url(r'^planning/sprint/new/submit/$', 'process_form', {'form_class': forms.SprintForm, 'home_name': 'web.planning_new_sprint'}, name='web.planning_new_sprint_submit'),
    url(r'^planning/sprint/availability/submit/(?P<params>\w+)/$', 'process_formset', {'form_class': forms.AvailabilityForm, 'home_name': 'web.planning_sprint_availability'}, name='web.planning_sprint_availability_submit'),
    url(r'^planning/sprint/stories/owner/submit/(?P<params>\w+)/$', 'process_formset', {'form_class': forms.TaskOwnerForm, 'home_name': 'web.planning_sprint_stories_owner'}, name='web.planning_sprint_stories_owner_submit'),

    # Custon
    url(r'^tabbed-view/(?P<id>\d+)/$', 'tabbed_view', name='web.tabbed_view'),
)
