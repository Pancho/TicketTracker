import ply
import ply.lex as lex

t_ignore = ''

tokens = (
	'LBRACKET',
	'RBRACKET',
	'EQUALS',
	'MINUS',
	'SPACE',
	'TEXT',
	'TAG',
	'PERSON',
	'NUMBER',
	'NEWLINE',
	)
	
	
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS =   r'='
t_MINUS =    r'-'
t_TAG =      r'\#[\d\w_]*'
t_PERSON =   r'\@[\d\w_]*'
t_TEXT =     r'[^\[\]=\-\n\ \#0-9\@][^\[\]=\-\n\ \#\@]*'	# text can't start with a number, but can be continued with one
t_NUMBER =   r'\d+'
t_NEWLINE =  r'\n'
t_SPACE = r'\ '

'''
def t_TEXT(t):
	r'[^\[\]=\-\n0-9\s]+'
#	t.value
	return t	
'''

lexer = lex.lex()
 	