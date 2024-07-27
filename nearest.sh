 cat <<EOF | psql pubcrawler
        SELECT p.name, p.address, l.lat, l.lon, p.rating from pub p, distance d, location l
        WHERE p.id = l.pub_id
        AND p.rating is not null
        AND l.lat between '51.50' AND '51.51'
        AND l.lon between '-0.28' and '-0.27'
        GROUP BY p.id, l.lat, l.lon
        order by p.rating DESC
        LIMIT 15
EOF
