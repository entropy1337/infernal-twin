#!/bin/bash

wget https://github.com/entropy1337/radiusd_copy/raw/master/freeradius-server-2.1.11.tar.bz2
wget https://raw.githubusercontent.com/entropy1337/radiusd_copy/master/freeradius-wpe.patch
tar -jxvf freeradius-server-2.1.11.tar.bz2
cd freeradius-server-2.1.11
patch -p1 < ../freeradius-wpe.patch
./configure
make
sudo make install
sh /usr/local/etc/raddb/certs/bootstrap
rm -rf freeradius*
