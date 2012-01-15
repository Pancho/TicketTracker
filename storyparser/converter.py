
import yacc
import web.models as wm

class Converter(object):
	def __init__(self):
		pass


	@staticmethod
	def django_task_to_task(django_task):
		dt = django_task
		task = yacc.Task(dt.description)
		task.score = dt.score
		if dt.state is None:
			pass	
		elif dt.state == "TO_CLOSED":
			task.tags.append("#closed")
		elif dt.state == "TO_WORKING":
			task.tags.append("#work")
		elif dt.state == "TO_WAITING":
			# waiting means no tag
			pass
		else:
			raise Exception("Unknown task.state: %s" % dt.state)
		if dt.owner:
			task.owner = "@" + dt.owner.username
		return task
	
	@staticmethod
	def django_story_to_text(django_story, django_tasks):
		'''
			Input:
				- story = web.Story
				- tasks = [list of web.Task]
			Output:
				- unicode representation of the story
		'''
		tasks = []
		for dt in django_tasks:
			task = Converter.django_task_to_task(dt)
			tasks.append(task)
			
		if django_story.tags:
			story_tags = django_story.tags.split(" ")
		else:
			story_tags = []
		
		story = yacc.Story(django_story.title, django_story.story_description, tasks, story_tags)
		
		if django_story.is_green:
			story.tags.append("#green")
		if django_story.is_burning:
			story.tags.append("#fire")
			
		
		if django_story.moscow:
			if django_story.moscow == "M":
				story.tags.append("#must")		
			elif django_story.moscow == "S":
				story.tags.append("#should")		
			elif django_story.moscow == "C":
				story.tags.append("#could")		
			elif django_story.moscow == "W":
				story.tags.append("#would")		
			else:
				raise Exception("Unknown MOSCOW state: %s" % django_story.moscow)
		
		if django_story.time_boxed:
			story.tags.append("#timebox")
			
				
		return story.to_text()
	
	
	
	@staticmethod
	def text_to_django_story(text):
		parser = yacc.get_parser('story') # we are testing just part of the parser
		if text[-1] != "\n":	# fix it a bit so parser works better
			text += "\n"
		story = parser.parse(text, tracking = True)
		dstory = wm.Story()
		dstory.title = story.title
		dstory.story_description = story.description
		
		dstory_tags_list = []
		for t in story.tags:
			if "#green" == t:
				dstory.is_green = True
			elif "#fire" == t:
				dstory.is_burning = True
			elif "#timebox" == t:
				dstory.time_boxed = True
			elif "#would" == t:
				dstory.moscow = "W"
			elif "#could" == t:
				dstory.moscow = "C"
			elif "#should" == t:
				dstory.moscow = "S"
			elif "#must" == t:
				dstory.moscow = "M"
			else:
				dstory_tags_list.append(t)
		dstory.tags = " ".join(dstory_tags_list)
		
		
		dtasks = []
		for task in story.tasks:
			dtask = wm.Task()
			dtask.score = task.score
			dtask.description = task.text.text
			tags = []
			for t in task.tags:
				if t == "#closed":
					dtask.state = "TO_CLOSED"
				elif t == "#work":
					dtask.state = "TO_WORKING"
				else:
					tags.append(t)
			if tags:
				dtask.description += " [" + " ".join(tags) + "]"	
										
			if task.owner:
				# make sure we catch the right errors here
				dtask.owner = wm.User.objects.filter(username = task.owner)
			dtask.story = dstory
			dtasks.append(dtask)
		
		return (dstory, dtasks) 	
		
	
	
	
	
	
	
			