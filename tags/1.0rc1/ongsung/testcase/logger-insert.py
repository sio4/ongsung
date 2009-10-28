#!/usr/bin/env python

import httplib, urllib

webhost = 'localhost:8000'


def query(st, pr=None, se=None, uu=''):
	params = urllib.urlencode({'statement':st, 'priority':pr,
		'session':uu, 'serial':se})
	headers = {"Content-type":"application/x-www-form-urlencoded"}
	conn = httplib.HTTPConnection(webhost)
	conn.request("POST", "/logger/insert/", params, headers)
	response = conn.getresponse()
	data = response.read()
	conn.close()

	print '		%s %s' % (response.status, response.reason)
	print '		%s' % data

	return response.status,data.split()[0],data.split()[1]


command = 'test string...'

print '### start test...'

ret = query(st=command, pr='L', se=0)
session = ret[1]
serial = int(ret[2]) + 1
if  ret[0] < 400:
	print '# case-01: ok'
else:
	print '# case-01: failed -------------------------------------------'

ret = query(st=command, pr='L', se=serial, uu=session)
session = ret[1]
serial = int(ret[2]) + 1
if  ret[0] < 400:
	print '# case-01: ok'
else:
	print '# case-01: failed -------------------------------------------'

ret = query(st=command, pr='L', se=serial, uu=session)
session = ret[1]
serial = int(ret[2]) + 1
if  ret[0] < 400:
	print '# case-01: ok'
else:
	print '# case-01: failed -------------------------------------------'


#if query(command) < 404:
#	print '# case-02: ok'
#else:
#	print '# case-01: failed -------------------------------------------'
#
#if query("") == 404:
#	print '# case-03: ok'
#else:
#	print '# case-01: failed -------------------------------------------'
