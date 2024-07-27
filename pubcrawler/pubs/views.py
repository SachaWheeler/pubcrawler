from django.shortcuts import render

# Create your views here.
import folium
import networkx as nx
from geopy.distance import geodesic
from django.shortcuts import render
from django.views import View
# Update imports to include the Distance model
from .models import Pub, Distance

class PubPathView(View):
    template_name = 'pubs/pub_path.html'

    def get(self, request):
        start_lat = float(request.GET.get('start_lat'))
        start_lon = float(request.GET.get('start_lon'))
        end_lat = float(request.GET.get('end_lat'))
        end_lon = float(request.GET.get('end_lon'))

        pubs = Pub.objects.all()
        G = nx.Graph()

        for pub in pubs:
            G.add_node(pub.fas_id, pos=(pub.latitude, pub.longitude))

        # Add distances to the graph
        distances = Distance.objects.all()
        for distance in distances:
            if distance.walking_distance:  # Ensure there is a walking distance
                G.add_edge(distance.pub1.fas_id, distance.pub2.fas_id, weight=distance.walking_distance)

        start_node = 'start'
        end_node = 'end'
        G.add_node(start_node, pos=(start_lat, start_lon))
        G.add_node(end_node, pos=(end_lat, end_lon))

        for node, data in G.nodes(data=True):
            if node not in [start_node, end_node]:
                G.add_edge(start_node, node, weight=geodesic((start_lat, start_lon), data['pos']).meters)
                G.add_edge(end_node, node, weight=geodesic((end_lat, end_lon), data['pos']).meters)

        paths = list(nx.shortest_simple_paths(G, source=start_node, target=end_node, weight='weight'))
        shortest_3_paths = paths[:3]

        m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

        for pub in pubs:
            folium.Marker(location=(pub.latitude, pub.longitude), popup=pub.name).add_to(m)

        folium.Marker(location=(start_lat, start_lon), popup='Start Point', icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=(end_lat, end_lon), popup='End Point', icon=folium.Icon(color='red')).add_to(m)

        colors = ['blue', 'purple', 'orange']
        for i, path in enumerate(shortest_3_paths):
            path_coords = [G.nodes[node]['pos'] for node in path]
            folium.PolyLine(locations=path_coords, color=colors[i], weight=5, opacity=0.7, popup=f'Path {i+1}').add_to(m)

        map_html = m._repr_html_()

        return render(request, self.template_name, {'map_html': map_html})

