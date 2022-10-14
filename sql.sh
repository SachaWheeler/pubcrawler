 cat <<EOF | psql pubcrawler
        SELECT p.name, p.address, d.distance from pub p, distance d
        WHERE p.id = d.end_loc
        AND d.start_loc = 11189
        ORDER BY d.distance
        LIMIT 10
EOF
