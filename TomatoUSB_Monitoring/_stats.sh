#!/bin/sh

dir=`dirname $0`

nice -n -19 $dir/cpu.sh
sleep 1
nice -n -19 $dir/mem.sh
sleep 1
nice -n -19 $dir/net.sh
sleep 1
nice -n -19 $dir/ping.sh
sleep 1
nice -n -19 $dir/assoclist.sh

