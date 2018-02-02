#!/opt/bin/bash

dir=`dirname $0`

name="router_ping_ext"
columns="dst ms"

pingdest="8.8.4.4"
p1="$pingdest"
p2=`ping -c1 -W1 $pingdest | grep 'seq=' | sed 's/.*time=\([0-9]*\.[0-9]*\).*$/\1/'`
points="$p1 $p2"
$dir/todb.sh "$name" "$columns" "$points"


