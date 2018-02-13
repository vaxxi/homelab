#!/bin/sh

dir=`dirname $0`

name="router_temp"
columns="temp_24"
p1=`wl -i eth1 phy_tempsense | awk '{ print $1 * .5 + 20 }'` # 2.4GHz
points="$p1"
echo "$name" "$columns" "$points"

$dir/todb.sh "$name" "$columns" "$points"

