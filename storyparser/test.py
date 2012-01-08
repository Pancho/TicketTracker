from pprint import pprint
import unittest
import logging

import lexer

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


	def test_newline(self):
		res = self.tokenize("#tag\n-")	
		self.assertEqual(repr(res), "[LexToken(TAG,'#tag',1,0), LexToken(NEWLINE,'\\n',1,4), LexToken(MINUS,'-',1,5)]")



if __name__ == '__main__':
	logging.basicConfig(level = logging.INFO)
	logger = logging.getLogger(__name__)
	unittest.main()
	sys.exit(0)
