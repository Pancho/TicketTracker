import unittest, logging, os, sys

from django.test import TestCase



import storyparser.lexer as lexer
import storyparser.yacc as yacc
import storyparser.converter as converter
from storyparser.tests import compare_django_stories, compare_django_tasks
import web.models as wm

from storyparser.yacc import Story, TextLine
		
class ConverterDjango(TestCase):
	# for unittests that need access django's database
	def test_username_fail_resolve(self):
		story_text = "= a\nb\n-c [@a]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c  [@a]")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)
		compare_django_tasks(self, rtasks, [dtask])

	def test_username_resolve(self):
		u = wm.User.objects.create(username = "andraz")
		story_text = "= a\nb\n-c [@andraz]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", owner = u)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		

