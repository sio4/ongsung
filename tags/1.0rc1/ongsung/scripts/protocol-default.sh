#!/bin/sh


cat |./manage.py shell <<EOF
from wall.models import *

try:
		Protocol.objects.get(name='telnet')
except:
		p = Protocol(name="telnet",port=23)
		p.save()

try:
		Protocol.objects.get(name='ssh')
except:
		p = Protocol(name="ssh",port=22)
		p.save()

from queman.models import *

try:
		Feature.objects.get(name='telnet')
except:
		f = Feature(name='telnet', description='telnet server')
		f.save()

try:
		Feature.objects.get(name='ssh')
except:
		f = Feature(name='ssh', description='ssh server')
		f.save()

quit()
EOF
