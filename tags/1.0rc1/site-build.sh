#!/bin/sh


python_version=2.6
django_dir="/var/lib/python-support/python$python_version/django"
site_root=/home/moyang


echo -n "install binaries... "
echo -n "mkdir, "
mkdir -p $site_root/bin
echo -n "build, "
make tunneld > make.log 2>&1
echo -n "tunneld, "
install -m755 -s tunneld $site_root/bin/
echo -n "ongsung-tunnel, "
install -m755 ongsung/ongsung-tunnel $site_root/bin/
echo -n "parse, "
sed -i "s,@TUNNEL_EXEC_PATH@,$site_root/bin,;s,@TUNNEL_EXEC_NAME@,tunneld," \
	$site_root/bin/ongsung-tunnel
echo "done."

echo "sync media for admin from dist..."
rsync -az $django_dir/contrib/admin/media/ $site_root/media/

echo "sync media for site/application from here..."
rsync -az media/ $site_root/media/


