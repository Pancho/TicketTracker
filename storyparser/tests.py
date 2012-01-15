from pprint import pprint
import unittest
import logging

import lexer
import yacc

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


from yacc import Story, TextLine

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
		self.assertEqual(repr(res), "Exception('Task is missing metadata in square brackets (line: 1, character: 5)',)")
		res = self.parse("-a []\n")
		self.assertEqual(repr(res), "Task(TextLine('a ',[]),[])")



if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	logger = logging.getLogger(__name__)
	unittest.main()
	sys.exit(0)
