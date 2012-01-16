import httplib
import urllib
import time
from xml.dom.minidom import parseString


text = '''<!DOCTYPE HTML>
<html>
		<title>Burndown Chart for Sprint 27, Named: We are back</title>
		<link rel="stylesheet" type="text/css" href="/media/css/default.css" />
		<link rel="stylesheet" type="text/css" href="/media/css/smoothness/jquery-ui-1.8.16.custom.css" />
		<link href='http://fonts.googleapis.com/css?family=Open+Sans+Condensed:300' rel='stylesheet' type='text/css' />
	</head>
	<body>
		<div id="tt-head">
			<ul>
				<li><a href="/login">Log In</a></li>
			</ul>
			<h1><a href="/">TicketTracker</a></h1>
		</div>
		<div id="tt-main">
			<div id="tt-burndownchart-lines"></div>
		</div>
	<script type="text/javascript" src="http://www.google.com/jsapi"></script>
		<script src="/media/js/jquery.js" type="text/javascript"></script>
		<script src="/media/js/jquery-ui-1.8.16.custom.min.js" type="text/javascript"></script>
		<script src="/media/js/tickettracker.js" type="text/javascript"></script>
	</body>
</html>'''


def call_w3c_validator(text):
	time.sleep(2) # W3C asks politely for 1 second break between requests, but I'll grant them 2 :)

	params = urllib.urlencode({'fragment': text, 'output': 'soap12'})
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

	conn = httplib.HTTPConnection('validator.w3.org')
	conn.request('POST', '/check', params, headers)
	response = conn.getresponse()
	data = response.read()

	root = parseString(data)

	print '--------------------------'
	print '-- W3C VALIDATOR REPORT --'
	print '--------------------------\n'
	print '%s (%s)' % (root.getElementsByTagName('m:doctype')[0].firstChild.data, 'Valid' if root.getElementsByTagName('m:validity')[0].firstChild.data == 'true' else 'Not Valid')

	print '\n\nERRORS:\n'
	for error in root.getElementsByTagName('m:error'):
		print '- Line: %s, Column: %s, Error: %s' % (error.getElementsByTagName('m:line')[0].firstChild.data, error.getElementsByTagName('m:col')[0].firstChild.data, error.getElementsByTagName('m:message')[0].firstChild.data)

	print'\n\nWARININGS:\n'
	for warning in root.getElementsByTagName('m:warning'):
		print '- %s' % warning.getElementsByTagName('m:message')[0].firstChild.data

	conn.close()


def call_htmllint(text):
	time.sleep(2) # Html lint service doesn't ask for any break between requests, but I'll grant them 2 seconds :)

#	params = urllib.urlencode({'source': text})
	params = urllib.urlencode({'source': text, 'tags_closeoptional': 'false'})
#	params = urllib.urlencode({'source': text, 'tags_whitespace': 'true'})
	headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

	conn = httplib.HTTPConnection('lint.brihten.com')
	conn.request('POST', '/html/lint/', params, headers)
	response = conn.getresponse()
	data = response.read()

	print '--------------------------'
	print '---- HTML LINT REPORT ----'
	print '--------------------------\n'

	print data

	conn.close()

def call_both():
	call_w3c_validator(text)
	call_htmllint(text)