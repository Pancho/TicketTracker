import ply.yacc as yacc

from lexer import tokens

class Story(object):
	def __init__(self, title, description, stories, tags):
		self.title = title
		self.description = description
		self.stories = stories
		self.tags = tags
	
	def __repr__(self):
		return u"Story(%s,%s,%s,%s)" % (repr(self.title), repr(self.description), repr(self.stories), repr(self.tags))

class Task(object):
	def __init__(self, text, taskmeta):
		self.text = text
		self.taskmeta = taskmeta

	def __repr__(self):
		return u"Task(%s,%s)" % (repr(self.text), repr(self.taskmeta))


class TextLine(object):
	def __init__(self, text = "", tags = []):
		self.text = text
		self.tags = tags

	def __repr__(self):
		return u"TextLine(%s,%s)" % (repr(self.text), self.tags)

#start = 'textualelement'

def p_expression_story(p):
	'story : storytitle NEWLINE storybody'
	p[0] = Story(p[1].text, p[3].text, [], p[1].tags + p[3].tags)

def p_expression_storytitle(p):
	'storytitle : EQUALS multispace textualelement'
	p[0] = p[3]

def p_expression_storybody(p):
	'storybody : textualelement'
	p[0] = p[1]

# textualelement is basically anything, tags are correctly parsed and propagated
# it can start with text or number or tag, [NOT space, minus, equals]

def p_expression_textualelement_b(p):
	'''	textualelement_b : TEXT
		textualelement_b : NUMBER
	'''
	p[0] = TextLine(p[1], [])

def p_expression_textualelement_b_tag(p):
	'textualelement_b : TAG'
	p[0] = TextLine(p[1], [p[1]])

def p_expression_textualelement(p):
	'textualelement : textualelement_b'
	p[0] = p[1]

def p_expression_textualelement2(p):
	'''	textualelement : textualelement SPACE
		textualelement : textualelement MINUS
		textualelement : textualelement EQUALS
	'''
	p[0] = p[1]
	p[0].text += p[2]

def p_expression_textualelement3(p):
	'textualelement : textualelement textualelement_b'
	p[0] = p[1]
	p[1].text += p[2].text
	p[1].tags += p[2].tags
	
	
	
# multispace
def p_expression_multispace1(p):
	'multispace : SPACE multispace'
	p[0] = p[1]
def p_expression_multispace2(p):
	'multispace : SPACE'
	p[0] = p[1]
def p_expression_multispace3(p):
	'multispace :'
	pass
	
	
def p_expression_taskdescription(p):
	'taskdescription : MINUS multispace textualelement'
	p[0] = p[3]

def p_expression_task(p):
	'task : taskdescription multispace taskmeta'
	p[0] = Task(p[1], p[3])
	
def p_expression_taskmeta(p):
	'taskmeta : LBRACKET textualelement RBRACKET'
	p[0] = p[2]

	
	
def p_error(p):
	print "AHAAAAAAA"
	raise Exception(repr(p))
	
def get_parser(start):
	return yacc.yacc(start=start)

	 