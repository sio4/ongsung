#!/usr/bin/env python

import httplib, urllib

webhost = 'localhost'


def query(command, feature, user):
	params = urllib.urlencode({'command':command, 'feature':feature,
		'user':user})
	headers = {"Content-type":"application/x-www-form-urlencoded"}
	conn = httplib.HTTPConnection(webhost)
	conn.request("POST", "/q/create/", params, headers)
	response = conn.getresponse()
	data = response.read()
	conn.close()

	print '		%s %s' % (response.status, response.reason)

	return response.status


command = 'by-testcase %s %s' % ('127.0.0.1', '8002')

print '### start test...'
if query(command, 'telnet', 2) < 400:
	print '# case-01: ok'
else:
	print '# case-01: failed -------------------------------------------'
if query('', 'telnet', 2) == 404:
	print '# case-02: ok'
else:
	print '# case-01: failed -------------------------------------------'
if query(command, '', 2) == 404:
	print '# case-03: ok'
else:
	print '# case-01: failed -------------------------------------------'
if query(command, 'telnet', '') == 404:
	print '# case-04: ok'
else:
	print '# case-01: failed -------------------------------------------'
