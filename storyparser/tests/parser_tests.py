from pprint import pprint
import unittest, logging, os, sys
# this is ugly beyond recognition, it is necessary as python does not have relative imports: we add parent dir to this one to the path
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../"))
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"


import storyparser.lexer as lexer
import storyparser.yacc as yacc
import storyparser.converter as converter
import web.models as wm

from storyparser.yacc import Story, TextLine


class Lexer(unittest.TestCase):
	
	def tokenize(self, s):
		lexer.lexer.input(s)
		l = []
		while True:
			tok = lexer.lexer.token()
			if not tok:
				break
			l.append(tok)
		return l
		
	def test1(self):
		res = self.tokenize("- abc")	
		self.assertEqual(repr(res), "[LexToken(MINUS,'-',1,0), LexToken(SPACE,' ',1,1), LexToken(TEXT,'abc',1,2)]")

	def test2(self):
		res = self.tokenize("- []")	
		self.assertEqual(repr(res), "[LexToken(MINUS,'-',1,0), LexToken(SPACE,' ',1,1), LexToken(LBRACKET,'[',1,2), LexToken(RBRACKET,']',1,3)]")

	def test_tag(self):
		res = self.tokenize("#tag")	
		self.assertEqual(repr(res), "[LexToken(TAG,'#tag',1,0)]")

		res = self.tokenize("#22")	
		self.assertEqual(repr(res), "[LexToken(TAG,'#22',1,0)]")

		res = self.tokenize("#")	
		self.assertEqual(repr(res), "[LexToken(TAG,'#',1,0)]")

		
	def test_number(self):
		res = self.tokenize("321 1")	
		self.assertEqual(repr(res), "[LexToken(NUMBER,'321',1,0), LexToken(SPACE,' ',1,3), LexToken(NUMBER,'1',1,4)]")

	def test_number(self):
		res = self.tokenize("a321 1")	
		self.assertEqual(repr(res), "[LexToken(TEXT,'a321',1,0), LexToken(SPACE,' ',1,4), LexToken(NUMBER,'1',1,5)]")


	def test_newline(self):
		res = self.tokenize("#tag\n-")	
		self.assertEqual(repr(res), "[LexToken(TAG,'#tag',1,0), LexToken(NEWLINE,'\\n',1,4), LexToken(MINUS,'-',1,5)]")



class Parser(unittest.TestCase):
	def parse(self, s):
		return self.parser.parse(s, tracking = True)
		
	def test_textline(self):
		self.parser = yacc.get_parser('textualelement') # we are testing just part of the parser
		
		res = self.parse("a")
		self.assertEqual(repr(res), "TextLine('a',[])")
		res = self.parse("a b")
		self.assertEqual(repr(res), "TextLine('a b',[])")
		
		# test tags
		res = self.parse("#ttt")
		self.assertEqual(repr(res), "TextLine('#ttt',['#ttt'])")
		res = self.parse("a#ttt")
		self.assertEqual(repr(res), "TextLine('a#ttt',['#ttt'])")
		res = self.parse("a#ttt#bbb")
		self.assertEqual(repr(res), "TextLine('a#ttt#bbb',['#ttt', '#bbb'])")

		# test persons
		res = self.parse("@ppp")
		self.assertEqual(repr(res), "TextLine('@ppp',['@ppp'])")
		res = self.parse("a@ppp")
		self.assertEqual(repr(res), "TextLine('a@ppp',['@ppp'])")
		res = self.parse("a@ppp@ddd")
		self.assertEqual(repr(res), "TextLine('a@ppp@ddd',['@ppp', '@ddd'])")

		# test other issues
		res = self.parse("32")
		self.assertEqual(repr(res), "TextLine('32',[])")
		res = self.parse("a=b")
		self.assertEqual(repr(res), "TextLine('a=b',[])")
		res = self.parse("a-b")
		self.assertEqual(repr(res), "TextLine('a-b',[])")
	
		# test startwithspace
		res = self.parse(" a")
		self.assertEqual(repr(res), "TextLine(' a',[])")
		
	
	def test_storytitle(self):
		self.parser = yacc.get_parser('storytitle') # we are testing just part of the parser
		res = self.parse("=a\n")
		self.assertEqual(repr(res), "TextLine('a',[])")
		# test spacing
		res = self.parse("= a\n")
		self.assertEqual(repr(res), "TextLine(' a',[])")
		res = self.parse("=  a\n")
		self.assertEqual(repr(res), "TextLine('  a',[])")
		res = self.parse("=  a \n")
		

	def test_storybody(self):
		self.parser = yacc.get_parser('storybody') # we are testing just part of the parser
		res = self.parse("description\n")
		self.assertEqual(repr(res), "TextLine('description',[])")

	def test_story(self):
		self.parser = yacc.get_parser('story') # we are testing just part of the parser
		res = self.parse("=st\ndescription\n")
		self.assertEqual(repr(res), "Story('st','description',[],[])")

		res = self.parse("=st#tag\ndescript#tag2 ion\n")
		self.assertEqual(repr(res), "Story('st#tag','descript#tag2 ion',[],['#tag', '#tag2'])")


		self.parser = yacc.get_parser('story') # we are testing just part of the parser
		res = self.parse("=st\ndescription line1\ndescription line 2\n")
		self.assertEqual(repr(res), "Story('st','description line1\\ndescription line 2',[],[])")
		self.parser = yacc.get_parser('story') # we are testing just part of the parser
		res = self.parse("=st\ndescription line1\n description line 2\n")
		self.assertEqual(repr(res), "Story('st','description line1\\n description line 2',[],[])")

		# test for tasks, buit no description
		res = self.parse("=st\n-a [1]\n")
		self.assertEqual(repr(res), "Story('st','',[Task(TextLine('a ',[]),[LexToken(NUMBER,'1',1,8)])],[])")



	def test_story_with_tasks(self):
		self.parser = yacc.get_parser('story') # we are testing just part of the parser
		res = self.parse("=st\ndescription\n-t1 [1]\n")
		self.assertEqual(repr(res), "Story('st','description',[Task(TextLine('t1 ',[]),[LexToken(NUMBER,'1',1,21)])],[])")
		res = self.parse("=st\ndescription\n-t1 [1 #tag1]\n")
		self.assertEqual(repr(res), "Story('st','description',[Task(TextLine('t1 ',[]),[LexToken(NUMBER,'1',1,21), LexToken(TAG,'#tag1',1,23)])],['#tag1'])")

	def test_taskdescription(self):
		self.parser = yacc.get_parser('taskdescription') # we are testing just part of the parser
		res = self.parse("-a")
		self.assertEqual(repr(res), "TextLine('a',[])")
		# test spacing
		res = self.parse("- a")
		self.assertEqual(repr(res), "TextLine(' a',[])")
		res = self.parse("-  a")
		self.assertEqual(repr(res), "TextLine('  a',[])")
		res = self.parse("-  a#tag")
		self.assertEqual(repr(res), "TextLine('  a#tag',['#tag'])")



	def test_taskmeta(self):
		self.parser = yacc.get_parser('taskmeta') # we are testing just part of the parser
		res = self.parse("[2]")
		self.assertEqual(repr(res), "[LexToken(NUMBER,'2',1,1)]")

	def test_taskdescription(self):
		self.parser = yacc.get_parser('taskdescription') # we are testing just part of the parser
		res = self.parse("- a")
		self.assertEqual(repr(res), "TextLine(' a',[])")


	def test_task(self):
		self.parser = yacc.get_parser('task') # we are testing just part of the parser
		res = self.parse("-a [2]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(NUMBER,'2',1,4)])")
		res = self.parse("-a  [2]\n")
		self.assertEqual(repr(res), "Task(TextLine('a  ',[]),[LexToken(NUMBER,'2',1,5)])")
		res = self.parse("-a [2 a]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(NUMBER,'2',1,4), LexToken(TEXT,'a',1,6)])")
		res = self.parse("-a [2  a]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(NUMBER,'2',1,4), LexToken(TEXT,'a',1,7)])")
		res = self.parse("-a [a 2]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(TEXT,'a',1,4), LexToken(NUMBER,'2',1,6)])")
		res = self.parse("-a [2 #tag]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(NUMBER,'2',1,4), LexToken(TAG,'#tag',1,6)])")
		res = self.parse("-a [2 @nick]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(NUMBER,'2',1,4), LexToken(PERSON,'@nick',1,6)])")

		self.assertRaises(IndexError, self.parse, "-a [2 2]\n")
		res = self.parse("-a [aa]\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[LexToken(TEXT,'aa',1,4)])")

		
		self.assertRaises(Exception, self.parse, "-a [aa =d]\n")

	def test_task_error(self):
		self.parser = yacc.get_parser('task') # we are testing just part of the parser
		res = self.parse("-a \n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[])")
		res = self.parse("-a []\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[])")


# these two methods are done as global and still having self, so we can actually rise right exceptions
# and at the same time call them from multiple classes
# we could also use multiple inheritance, but then it's harder to comprehend and trace what's happening
def compare_django_stories(self, ds1, ds2):
	self.assertEqual(ds1.title, ds2.title)
	self.assertEqual(ds1.story_description, ds2.story_description)
	self.assertEqual(ds1.is_burning, ds2.is_burning)
	self.assertEqual(ds1.time_boxed, ds2.time_boxed)
	self.assertEqual(ds1.is_green, ds2.is_green)
	self.assertEqual(ds1.moscow, ds2.moscow)
	
def compare_django_tasks(self, dts1, dts2):
	for n, dt1 in enumerate(dts1):
		dt2 = dts2[n]
		self.assertEqual(dt1.description, dt2.description)
		self.assertEqual(dt1.score, dt2.score)
		self.assertEqual(dt1.state, dt2.state)	
		self.assertEqual(dt1.owner, dt2.owner)	


class TestsConverter(unittest.TestCase):
	def test_django_story_to_text(self):
		dstory = wm.Story(title = "story_title", story_description = "story_description")
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title \nstory_description\n")

		dstory.is_green = True
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #green\nstory_description\n")
		dstory.is_green = False
		
		dstory.is_burning = True
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #fire\nstory_description\n")
		dstory.is_burning = False

		dstory.moscow = 'M'
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #must\nstory_description\n")
		dstory.moscow = 'S'
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #should\nstory_description\n")
		dstory.moscow = 'C'
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #could\nstory_description\n")
		dstory.moscow = 'W'
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #would\nstory_description\n")
		dstory.moscow = None
		
		dstory.tags = "#t1 #t2"
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= story_title #t1 #t2\nstory_description\n")
		dstory.title = "title with tag #t2" 	# here we make sure we don'd duplicate tags if they are already in the title
		res = converter.Converter.django_story_to_text(dstory, [])	
		self.assertEqual(res, "= title with tag #t2 #t1\nstory_description\n")
		dstory.tags = None
		dstory.title = "story_title"
		
		dtask = wm.Task(description = "task description")
		res = converter.Converter.django_story_to_text(dstory, [dtask])	
		self.assertEqual(res, "= story_title \nstory_description\n- task description\n")
		res = converter.Converter.django_story_to_text(dstory, [dtask, dtask])	
		self.assertEqual(res, "= story_title \nstory_description\n- task description\n- task description\n")


	def test_django_task_to_text(self):
		dtask = wm.Task(description = "task_description")
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description")

		dtask.state = "TO_CLOSED"
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description [#closed]")
		dtask.state = "TO_WORKING"
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description [#work]")
		dtask.state = "TO_WAITING"
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description")

		dtask.score = 5
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description [5]")

		from django.contrib.auth.models import User
		u = User(username = "duh")
		dtask.owner = u
		res = converter.Converter.django_task_to_task(dtask).to_text()	
		self.assertEqual(res, "- task_description [5 @duh]")


	
		
	def test_text_to_django_story(self):
		story_text = "= a\nb"
		dstory = wm.Story(title = " a", story_description = "b")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		

		story_text = "= a #fire\nb"
		dstory = wm.Story(title = " a #fire", story_description = "b", is_burning = True)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)

		story_text = "= a #timebox\nb"
		dstory = wm.Story(title = " a #timebox", story_description = "b", time_boxed = True)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)

		story_text = "= a #green\nb"
		dstory = wm.Story(title = " a #green", story_description = "b", is_green = True)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)


		story_text = "= a #must\nb"
		dstory = wm.Story(title = " a #must", story_description = "b", moscow = "M")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)
		story_text = "= a #should\nb"
		dstory = wm.Story(title = " a #should", story_description = "b", moscow = "S")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)
		story_text = "= a #could\nb"
		dstory = wm.Story(title = " a #could", story_description = "b", moscow = "C")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)
		story_text = "= a #would\nb"
		dstory = wm.Story(title = " a #would", story_description = "b", moscow = "W")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)

		# tricky... we need to figure out how to handle tag removal in the future, in order to sync from form to text
		story_text = "= a #t1 #t2\nb"
		dstory = wm.Story(title = " a #t1 #t2", story_description = "b", tags = "#t1 #t2")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)




	def test_text_to_django_story_with_tasks(self):
		story_text = "= a\nb\n-c"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		# empty taskmeta
		story_text = "= a\nb\n-c []"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		


		# score taskmeta
		story_text = "= a\nb\n-c [1]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", score = 1)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		# TEST USER - THIS ONE FAILS UNTIL PANCHO TELLS US WHERE THE @nick CAN BE RESOLVED
		'''
		story_text = "= a\nb\n-c [@a]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", score = 1)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		
		'''


		# tag 
		story_text = "= a\nb\n-c [#t1]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c  [#t1]")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		# tag plus score
		story_text = "= a\nb\n-c [#t1 1]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c  [#t1]", score = 1)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		


		# #closed
		story_text = "= a\nb\n-c [#closed]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", state = "TO_CLOSED")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		#closed
		story_text = "= a\nb\n-c [#work]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c ", state = "TO_WORKING")
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		# badass tag combo
		story_text = "= a\nb\n-c [1 #work #t1]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask = wm.Task(description = "c  [#t1]", state = "TO_WORKING", score = 1)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask])		

		# badass tag double combo
		story_text = "= a\nb\n-c [1 #work #t1]\n-d [2 #closed]"
		dstory = wm.Story(title = " a", story_description = "b")
		dtask1 = wm.Task(description = "c  [#t1]", state = "TO_WORKING", score = 1)
		dtask2 = wm.Task(description = "d ", state = "TO_CLOSED", score = 2)
		(rstory, rtasks) = converter.Converter.text_to_django_story(story_text)	
		compare_django_stories(self, rstory, dstory)		
		compare_django_tasks(self, rtasks, [dtask1, dtask2])		

		


if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	logger = logging.getLogger(__name__)
	unittest.main()
	sys.exit(0)
