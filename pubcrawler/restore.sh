#!/bin/bash

start=`date +%s`
SECONDS=0
local_dump=0
prod_backup=0
download=0
restore=0
migrate=0
if [ $# -ne 1 ]
then
    # echo "Usage: `basename $0` DUMP_FILE"
    date=$(date '+%Y-%m-%d_%H%M%S')
    echo $date

    # trap ctrl-c and call ctrl_c()
    trap ctrl_c INT

    function ctrl_c() {
        echo "** Trapped CTRL-C"
        rm "$local_backup_file"
    }

    # dump local
    echo "Dumping local db"
    local_backup_file="../databases/local.${date}.dump"
    pg_dump -Fc --no-acl --no-owner -h localhost  pubcrawler > "$local_backup_file"

    local_dump=$SECONDS
    SECONDS=0

else

    dump_file=$1

    echo -n "Are you sure you want to restore $dump_file locally (y/N)? "
    read answer

    # for Monster
    # pg_restore -j 12 --verbose --clean --no-acl -d jftportfolio ../databases/production.2024-06-05_060211.dump
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        pg_restore -j 12 --verbose --clean --no-acl -d pubcrawler "$dump_file"
    else
        echo "Quitting"
    fi
    restore=$SECONDS

fi

SECONDS=0
echo "migrating (if necessary)"
./manage.py migrate
migrate=$SECONDS

echo "Done"
say -v Kate "Complete"
end=`date +%s`

echo
if [ $local_dump -gt 0 ];  then echo "local dump : ${local_dump} secs"; fi
if [ $download -gt 0 ];    then echo "download   : ${download} secs"; fi
if [ $restore -gt 0 ];     then echo "restore    : ${restore} secs"; fi
if [ $migrate -gt 0 ];     then echo "migrate    : ${migrate} secs"; fi
total=$((local_dump + prod_backup + download + restore + migrate))
echo "total time : ${total} secs"

runtime=$((end-start))
echo "$runtime seconds"
