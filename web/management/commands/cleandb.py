from django.core.management import call_command
from django.db import connections
from django.core.management.base import AppCommand
from django.core.management.sql import sql_delete, sql_all

DEFAULT_DB_ALIAS = 'default'

class Command(AppCommand):
	help = 'This command helps you recreate a database from scratch. It drops everything, creates all the tables and invokes fixture import.'

	def handle_app(self, app, **options):
		db = options.get('database', DEFAULT_DB_ALIAS)
		verbosity = int(options.get('verbosity', 1))
		connection = connections[db]

		drop_queries = u'\n'.join(sql_delete(app, self.style, connection)).encode('utf-8')
		cursor = connection.cursor()
		for query in drop_queries.split(';'):
			if query != '':
				if verbosity:
					self.stdout.write('\n\nExecuting query\n%s' % query.strip())
				cursor.execute(query.strip())
		cursor.close()

		create_queries = u'\n'.join(sql_all(app, self.style, connection)).encode('utf-8')
		cursor = connection.cursor()
		for query in create_queries.split(';'):
			if query != '':
				if verbosity:
					self.stdout.write('\n\nExecuting query\n%s' % query.strip())
				cursor.execute(query.strip())
		cursor.close()

		call_command('loaddata', 'initial_data', verbosity = verbosity, database = db)