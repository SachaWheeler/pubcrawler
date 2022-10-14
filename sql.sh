 cat <<EOF | psql pubcrawler
 SELECT p.name, d.distance
 FROM pub p, distance d

 WHERE d.start_loc = 11206
 AND d.end_loc = p.id

 ORDER by distance
 LIMIT 10;
EOF
