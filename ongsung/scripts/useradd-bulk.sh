#!/bin/sh
#
# simple script for 'bulk' adding users from csv list.
#

cat |./manage.py shell <<EOF
from django.contrib.auth.models import *
import csv

ul = []
reader = csv.reader(open("/tmp/uploaded-file"))
for id,un,fn,ln,em,i_a,i_s,ll,dj in reader:
	if id == "id":
		continue
	try:
		u = User.objects.get(username__exact=un)
	except:
		u = User(username=un)
		u.first_name = fn
		u.last_name = ln
		u.email = em
		u.is_active = False
		u.is_staff = False
	ul.append(u)

for u in ul:
	if u.id == None:
		u.save()
		u = User.objects.get(username__exact=u.username)
		print u.id,u.username,u.last_name,u.first_name,u.email

quit()
EOF
