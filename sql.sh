 cat <<EOF | psql pubcrawler
        SELECT p.name, p.address, l.lat, l.lon

        FROM pub p, location l
        WHERE p.id = l.pub_id
        AND (l.lat BETWEEN 51.492848 AND 51.501888)
        AND (l.lon BETWEEN -0.1909 AND -0.18186)
        LIMIT 10
EOF
