#!/bin/sh

start=`date +%s`
SECONDS=0
local_dump=0
prod_backup=0
download=0
restore=0
migrate=0
if [ $# -ne 1 ]
then
    echo "Usage: `basename $0` DUMP_FILE"
else
    dump_file=$1

    echo -n "Are you sure you want to restore $dump_file locally (y/N)? "
    read answer

    if [ "$answer" != "${answer#[Yy]}" ] ;then
        pg_restore -j 12 --verbose --clean --no-acl --no-owner -h localhost -d pubcrawler "$dump_file"
    else
        echo "Quitting"
    fi
    restore=$SECONDS

fi

echo "Done"
say -v Victoria "Done restoring database"
