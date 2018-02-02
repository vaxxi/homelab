#!/opt/bin/bash

dir=`dirname $0`

name="router_cpu"
columns="usr sys nic idle io irq sirq"
points=`top -bn1 | head -3 | awk '/CPU/ {print $2,$4,$6,$8,$10,$12,$14}' | sed 's/%//g'`
$dir/todb.sh "$name" "$columns" "$points"

