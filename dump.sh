#!/bin/sh

date=$(date '+%Y-%m-%d_%H%M%S')
echo $date

# dump local
echo "Dumping local db"
local_backup_file="./databases/db.${date}.dump"
pg_dump -Fc --no-acl --no-owner -h localhost pubcrawler > "$local_backup_file"

echo "Done"
say -v Victoria "Done dumping database"
