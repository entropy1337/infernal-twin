#!/bin/bash

wget ftp://ftp.freeradius.org/pub/radius/old/freeradius-server-2.1.11.tar.bz2
wget http://www.opensecurityresearch.com/files/freeradius-wpe-2.1.11.patch
tar -jxvf freeradius-server-2.1.11.tar.bz2
cd freeradius-server-2.1.11
patch -p1 < ../freeradius-wpe-2.1.11.patch
./configure
make
sudo make install
sh /usr/local/etc/raddb/certs/bootstrap
rm -rf freeradius*
