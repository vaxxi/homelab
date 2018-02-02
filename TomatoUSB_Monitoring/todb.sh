#/opt/bin/bash

dbname="telegraf"
dbhost="85.90.244.165:8086"
user="vaxxi"
passwd="gePQPmQBaqhZJMAM"

if [ $# -ne 3 ]; then
    echo "Usage: $0 \"series name\" \"columns\" \"points\""
    exit
fi

#name="\"$1\""
#columns=`echo $2 | sed 's/^\(.*\)$/"\1"/' | sed 's/ /","/g'`
#points=`echo $3 | sed 's/\([a-zA-Z0-9\.]*[a-zA-Z][a-zA-Z0-9\.]*\)/"\1"/g' | sed 's/ /,/g'`

#payload=`cat` <<- EOT
#    [{
#      "name":$name,
#      "columns":[$columns],
#      "points":[[$points]]
#    }]
#EOT

name="rtn16"

IFS=' ' read -r -a cols <<< "$2"
IFS=' ' read -r -a vals <<< "$3"

payload=''

for index in "${!cols[@]}"
do
payload+="${cols[index]},host=${name} value=${vals[index]}"
payload+=$'\n'
done

# echo ${payload}

/opt/bin/curl -s -i -XPOST "http://$dbhost/write?db=$dbname&u=$user&p=$passwd" --data-binary "${payload}" > /dev/null

