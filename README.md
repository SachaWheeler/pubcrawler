# pubcrawler

PLots a route between 2 locations (lat, lon) stopping at every nice pub along the way.

config.py
- pub object
create_tables.py
- import Pub and Location data to DB
extended_data.py
- add ratings etc.
insert_data.py
- fill Pub table
load_osm.py
- draw maps
plot_path.py
- paths between START and END points
process_distances.py
- calculations on curved surface
process_walking_distances.py
- distance via surface streets
save_maps.py
- download maps from API
test_distances.py
- maps
