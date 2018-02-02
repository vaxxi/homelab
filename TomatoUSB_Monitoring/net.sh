#!/opt/bin/bash

maxint=4294967295
dir=`dirname $0`
scriptname=`basename $0`
old="/opt/tmp/$scriptname.data.old"
new="/opt/tmp/$scriptname.data.new"
old_epoch_file="/opt/tmp/$scriptname.epoch.old"

old_epoch=`cat $old_epoch_file`
new_epoch=`date "+%s"`
echo $new_epoch > $old_epoch_file

interval=`expr $new_epoch - $old_epoch` # seconds since last sample

name="router_net"
columns="recv_mbps recv_errs recv_drop trans_mbps trans_errs trans_drop"

if [ -f $new ]; then
    awk -v old=$old -v interval=$interval -v maxint=$maxint '{
        getline line < old
        split(line, a)
        if( $1 == a[1] ) {
            recv_bytes  = $2 - a[2]
            trans_bytes = $5 - a[5]
            if(recv_bytes < 0) {recv_bytes = recv_bytes + maxint}    # maxint counter rollover
            if(trans_bytes < 0) {trans_bytes = trans_bytes + maxint} # maxint counter rollover
            recv_mbps  = (8 * (recv_bytes) / interval) / 1048576     # mbits per second
            trans_mbps = (8 * (trans_bytes) / interval) / 1048576    # mbits per second
            columns="$1_rx $1_rxerr $1_rxdrop $1_tx $1_txerr $1_txdrop"
            print $1, recv_mbps, $3 - a[3], $4 - a[4], trans_mbps, $6 - a[6], $7 - a[7]
        }
    }' $new  | while read line; do
        points="$line"

	pa=($points)
	interface="${pa[0]}"
	columns="${interface}_rx ${interface}_rxerr ${interface}_rxdrop ${interface}_tx ${interface}_txerr ${interface}_txdrop"
	points="${pa[1]} ${pa[2]} ${pa[3]} ${pa[4]} ${pa[5]} ${pa[6]}"
        $dir/todb.sh "$name" "$columns" "$points"
        sleep 1
    done
    mv $new $old
fi

cat /proc/net/dev | tail +3 | tr ':|' '  ' | awk '{print $1,$2,$4,$5,$10,$12,$13}' > $new

