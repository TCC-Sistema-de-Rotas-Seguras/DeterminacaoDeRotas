import folium
import osmnx as ox
import Crimes

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.724249554085418, -46.57659561047842)
Graph_radio = 1000
BOs_folder = "./Data/Bos/"
Graph_filename = "Graph.graphml"

# ____ Localização de Crimes____
Locations = Crimes.CrimeLocations(BOs_folder)
FilteredLocations = Crimes.FilterCrimes(Graph_Location, Graph_radio, Locations)

# ____ Geração do Grafo ____
Graph = ox.graph.graph_from_point(Graph_Location, dist=Graph_radio, network_type="drive")

# Aplicando peso dos crimes no grafo 
Graph = Crimes.CrimeAplication(Graph, FilteredLocations)

# Obter os hotspots de crimes
hotspots = Crimes.GraphConversionToHotSpots(Graph)

# Calcula o centro do mapa baseado na média das coordenadas
center_lat = sum(lat for lat, lon in hotspots) / len(hotspots)
center_lon = sum(lon for lat, lon in hotspots) / len(hotspots)

# Cria o mapa centralizado
m = folium.Map(location=[center_lat, center_lon], zoom_start=20)

# Adiciona os hotspots ao mapa
for lat, lon in hotspots:
    folium.CircleMarker(
        location=[lat, lon],
        radius=20,  # Tamanho do círculo
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.6,
        popup=f"Hotspot: ({lat}, {lon})",
    ).add_to(m)

# Salva o mapa em um arquivo HTML
m.save("hotspots_map.html")