import unittest, logging, os, sys

from django.test import TestCase

import storyparser.lexer as lexer
import storyparser.yacc as yacc
import storyparser.converter as converter
import web.models as wm

from storyparser.yacc import Story, TextLine
		
class ConverterDjango(TestCase):
	# for unittests that need access django's database
	def test_username_fail_resolve(self):
		story_text = "= a\nb\n-c [@a]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", score = 1)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		self.check_django_stories(rstory, dstory)		
		self.check_django_tasks(rtasks, [dtask])		

		

