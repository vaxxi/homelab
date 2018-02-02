#/opt/bin/bash

dbname="DB_NAME"
dbhost="DB_HOSTNAME_AND_PORT"
user="DB_USER"
passwd="DB_PASSWORD"

if [ $# -ne 3 ]; then
    echo "Usage: $0 \"series name\" \"columns\" \"points\""
    exit
fi

name="ROUTER_NAME"

IFS=' ' read -r -a cols <<< "$2"
IFS=' ' read -r -a vals <<< "$3"

payload=''

for index in "${!cols[@]}"
do
payload+="${cols[index]},host=${name} value=${vals[index]}"
payload+=$'\n'
done

/opt/bin/curl -s -i -XPOST "http://$dbhost/write?db=$dbname&u=$user&p=$passwd" --data-binary "${payload}" > /dev/null

