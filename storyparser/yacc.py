import ply.yacc as yacc
import logging

from lexer import tokens, t_NUMBER

class Story(object):
	def __init__(self, title, description, tasks, tags):
		self.title = title
		self.description = description
		self.tasks = tasks
		self.tags = tags
	
	def __repr__(self):
		return u"Story(%s,%s,%s,%s)" % (repr(self.title), repr(self.description), repr(self.tasks), repr(self.tags))


	def parse_taskmeta(self, taskmeta_list):
		# this isn't really taskmeta but more anything between the brackets
		self.taskmeta_list = taskmeta_list
	
		for el in taskmeta_list:
			if el.type == 'TAG':
				self.tags.append(el.value)
			else:
				logging.error("Unknown token inside the story metadata: %s" % (repr(el)))
				
				raise SyntaxError

	def to_text(self):	
		lines = []
		# make sure we don't duplicate tags that are already in the title
		# and make sure they are unique
		new_tags = []
		for t in self.tags:
			try:
				self.title.index(t)
			except ValueError: # this means it is not in there
				if t not in new_tags: # this is small number, so linear scan is faster than set/dict
					new_tags.append(t)
		
		
		tags = " ".join(new_tags)		# make unique
		lines.append("=%s" % (self.title,))
		if tags:
			lines.append("[%s]" % (tags,))
		if self.description:
			lines.append(self.description)
		for t in self.tasks:
			lines.append(t.to_text())
		lines.append("") # we always finish with a new line!
		return "\n".join(lines)

class Task(object):
	def __init__(self, text):
		self.text = text
		self.tags = []
		self.score = None
		self.owner = None
		self.taskmeta_list = []
		
	def parse_taskmeta(self, taskmeta_list):
		self.taskmeta_list = taskmeta_list
	
		for el in taskmeta_list:
			if el.type == 'NUMBER': 
				if self.score:
					logging.error("Task metadata includes more than one number!")
					raise SyntaxError #("Task metadata includes more than one number!")
				self.score = int(el.value)
			elif el.type == 'PERSON': 
				if self.owner:
					logging.error("Task metadata includes more than one owner!")
					raise SyntaxError #("Task metadata includes more than one number!")
				self.owner = el.value
			elif el.type == 'TAG':
				self.tags.append(el.value)
			elif el.type == 'TEXT':
				self.tags.append(el.value)
			else:
				logging.error("Unknown token inside the task metadata: %s" % (repr(el)))
				
				raise SyntaxError
#		if not self.score:
#			logging.error("Task matadata must include exactly one number (score)")
#			raise SyntaxError

			
	def __repr__(self):
		return u"Task(%s,%s)" % (repr(self.text), repr(self.taskmeta_list))

	def to_text(self):
		taskmeta_str_list = []
		if self.score:
			taskmeta_str_list.append(unicode(self.score))
		for t in list(set(self.tags)):
			taskmeta_str_list.append(t)
		if self.owner:	
			taskmeta_str_list.append(self.owner)
		
		a = "-" + self.text 
		if taskmeta_str_list:
			taskmeta_string = " ".join(taskmeta_str_list)
			
			a += "[" + taskmeta_string + "]" 
		return a


class TextLine(object):
	def __init__(self, text = "", tags = []):
		self.text = text
		self.tags = tags

	def __repr__(self):
		return u"TextLine(%s,%s)" % (repr(self.text), self.tags)

#start = 'textualelement'

def p_expression_story(p):
	'story : storytitle storybody'
	p[0] = Story(p[1].text, p[2].text, [], p[1].tags + p[2].tags)

# i think the following is a bit hackish, but will do for now
def p_expression_story3(p):
	'story : storytitle taskmeta NEWLINE storybody'
	p[0] = Story(p[1].text, p[4].text, [], p[1].tags + p[4].tags)
	p[0].parse_taskmeta(p[2])

def p_expression_story2(p):
	'story : storytitle'
	p[0] = Story(p[1].text, "", [], p[1].tags)


def p_expression_story_with_tasks(p):
	'story : story task'
	p[0] = p[1]
	p[0].tasks.append(p[2])
	#p[0].tags.extend(p[2].tags)	# do not add tags from tasks to story tags

def p_expression_storytitle(p):
	'storytitle : EQUALS textualelement NEWLINE'
	p[0] = p[2]



def p_expression_storybody(p):
	'storybody : textualelement NEWLINE'
	p[0] = p[1]

def p_expression_storybody2(p):
	'storybody : storybody storybody'
	p[0] = p[1]
	p[0].text += "\n" + p[2].text
	p[0].tags.extend(p[2].tags)

# make sure storybody can have newlines at the end
def p_expression_storybody3(p):
	'storybody : storybody NEWLINE'
	p[0] = p[1]
	p[0].text += "\n"


# textualelement is basically anything, tags are correctly parsed and propagated
# it can start with text or number or tag, [NOT minus, equals]

def p_expression_textualelement_b(p):
	'''	textualelement_b : TEXT
		textualelement_b : NUMBER
		textualelement_b : SPACE
	'''
	p[0] = TextLine(p[1], [])

def p_expression_textualelement_b_tag(p):
	'''
		textualelement_b : TAG
		textualelement_b : PERSON
	'''
	p[0] = TextLine(p[1], [p[1]])

def p_expression_textualelement(p):
	'textualelement : textualelement_b'
	p[0] = p[1]

def p_expression_textualelement2(p):
	'''	
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
	'multispace_some : SPACE multispace_some'
	p[0] = p[1] + p[2]
def p_expression_multispace2(p):
	'multispace_some : SPACE'
	p[0] = p[1]
#def p_expression_multispace3(p):
#	'multispace : multispace_some'
#	p[0] = p[1]

# since texutalelement takes spaces, we don't have a need for zero-length multispaces
#def p_expression_multispace4(p):
#	'multispace :'
#	pass
	

def p_expression_task(p):
	'''
		task : taskdescription taskmeta NEWLINE
		task : taskdescription taskmeta multispace_some NEWLINE
	'''
	p[0] = Task(p[1])
	p[0].parse_taskmeta(p[2])

# we allow also leaving out taskmeta entirely
def p_expression_task_no_taskmeta(p):
	'task : taskdescription NEWLINE'
	p[0] = Task(p[1])

def p_expression_taskdescription(p):
	'taskdescription : MINUS textualelement'
	p[0] = p[2]

def p_expression_taskmeta(p):
	'taskmeta : LBRACKET taskmeta_list RBRACKET'
	p[0] = p[2]

def p_expression_taskmeta_problem(p):
	'taskmeta : LBRACKET error RBRACKET'
	logging.error("Task metadata cannot be parsed correctly (line: %i, character: %i)" % (p.lexer.lineno, p.lexer.lexpos))					
	raise Exception("Task metadata cannot be parsed correctly (line: %i, character: %i)" % (p.lexer.lineno, p.lexer.lexpos))


def p_expression_taskmeta_list_empty(p):
	'''
		taskmeta_list : 
	'''
	p[0] = []

def p_expression_taskmeta_list(p):
	'''
		taskmeta_list : TEXT
		taskmeta_list : TAG
		taskmeta_list : NUMBER
		taskmeta_list : PERSON
	'''
	p[0] = [p.slice[1]]

def p_expression_taskmeta_list2(p):
	'''
		taskmeta_list : taskmeta_list multispace_some TEXT
		taskmeta_list : taskmeta_list multispace_some TAG
		taskmeta_list : taskmeta_list multispace_some NUMBER
		taskmeta_list : taskmeta_list multispace_some PERSON
	'''
	p[0] = p[1]
	p[0].append(p.slice[3])
	
	


	

	
def p_error(p):
	'''
	while 1:
		tok = yacc.token()             # Get the next token
		if not tok or tok.type == 'NEWLINE':
			break
		yacc.restart()
	'''	        
	#raise Exception(repr(p))
	pass
	
def get_parser(start):
	return yacc.yacc(start=start)

	 