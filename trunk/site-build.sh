#!/bin/sh


python_version=2.6
django_dir="/var/lib/python-support/python$python_version/django"
site_root=/home/moyang


echo "install binaries..."
mkdir -p $site_root/bin
make tunneld > make.log 2>&1
install -m755 -s tunneld $site_root/bin/
install -m755 ongsung/ongsung-tunnel $site_root/bin/
sed -i "s,@TUNNEL_EXEC_PATH@,$site_root/bin,;s,@TUNNEL_EXEC_NAME@,tunneld," \
	$site_root/bin/ongsung-tunnel

echo "sync media for admin from dist..."
rsync -az $django_dir/contrib/admin/media/ $site_root/media/

echo "sync media for site/application from here..."
rsync -az media/ $site_root/media/


