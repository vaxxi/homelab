#!/bin/sh

dir=`dirname $0`

name="router_temp"
columns="temp_24 temp_50"
p1=`wl -i eth1 phy_tempsense | awk '{ print $1 * .5 + 20 }'` # 2.4GHz
p2=`wl -i eth2 phy_tempsense | awk '{ print $1 * .5 + 20 }'` # 5.0GHz
points="$p1 $p2"
echo "$name" "$columns" "$points"

$dir/todb.sh "$name" "$columns" "$points"

