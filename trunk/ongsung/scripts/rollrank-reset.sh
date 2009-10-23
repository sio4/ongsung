#!/bin/sh


cat |./manage.py shell <<EOF

from blog.models import Roll

for r in Roll.objects.all():
	r.rank = 0
	r.save()

quit()
EOF
