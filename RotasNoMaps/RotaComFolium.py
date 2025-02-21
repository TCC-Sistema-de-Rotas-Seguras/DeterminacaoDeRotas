import osmnx as ox
import networkx as nx
import folium
from shapely.geometry import Point, LineString
from geopy.distance import geodesic

# Configurações iniciais
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros
ox.settings.bidirectional_network_types += "drive"
G = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Área a ser evitada
avoid_location = (-23.72456530977091, -46.574473368105146)  # Coordenadas da área a evitar
avoid_radius = 200  # Raio da área a ser evitada (em metros)

# Ajustar pesos das arestas na área a ser evitada
avoid_point = Point(avoid_location[1], avoid_location[0])
G_modified = G.copy()

for u, v, data in G_modified.edges(data=True):
    u_point = Point(G.nodes[u]["x"], G.nodes[u]["y"])
    v_point = Point(G.nodes[v]["x"], G.nodes[v]["y"])
    # Verifica se a aresta cruza a área a ser evitada
    if u_point.distance(avoid_point) < avoid_radius / 1000 or v_point.distance(avoid_point) < avoid_radius / 1000:
        data["length"] *= 10  # Aumenta o peso da aresta

# Função heurística para o A* (distância geodésica entre dois nós)
def heuristic(node1, node2):
    coord1 = (G.nodes[node1]["y"], G.nodes[node1]["x"])
    coord2 = (G.nodes[node2]["y"], G.nodes[node2]["x"])
    return geodesic(coord1, coord2).meters

# Definir origem e destino
origin_point = (-23.72414295696128, -46.57761691709549)
destination_point = (-23.725213569653757, -46.56954883239719)

# Encontrar os nós mais próximos no grafo modificado
orig_node = ox.distance.nearest_nodes(G_modified, origin_point[1], origin_point[0])
dest_node = ox.distance.nearest_nodes(G_modified, destination_point[1], destination_point[0])

# Encontrar a rota mais curta usando o A*
route = nx.astar_path(G_modified, orig_node, dest_node, heuristic=heuristic, weight="length")

# Criar um mapa com Folium
m = folium.Map(location=Fei_Location, zoom_start=15, tiles="CartoDB Positron")

# Adicionar a área evitada (círculo vermelho)
folium.Circle(
    location=avoid_location,
    radius=avoid_radius,
    color="red",
    fill=True,
    fill_color="red",
    fill_opacity=0.3,
    popup="Área Evitada"
).add_to(m)

# Adicionar ponto de origem (marcador verde)
folium.Marker(
    location=origin_point,
    popup="Origem",
    icon=folium.Icon(color="green", icon="play")
).add_to(m)

# Adicionar ponto de destino (marcador azul)
folium.Marker(
    location=destination_point,
    popup="Destino",
    icon=folium.Icon(color="blue", icon="flag")
).add_to(m)

# Desenhar a rota sobre as ruas corretas
for u, v, data in G_modified.edges(data=True):
    if "geometry" in data:
        # Se a aresta tiver geometria, usa a linha real da rua
        line_coords = [(lat, lon) for lon, lat in data["geometry"].coords]
    else:
        # Caso contrário, desenha uma linha reta entre os nós
        line_coords = [(G.nodes[u]["y"], G.nodes[u]["x"]), (G.nodes[v]["y"], G.nodes[v]["x"])]

    folium.PolyLine(
        line_coords, color="gray", weight=1, opacity=0.5
    ).add_to(m)

# Adicionar a rota calculada (agora seguindo as ruas corretamente)
route_lines = []
for i in range(len(route) - 1):
    u, v = route[i], route[i + 1]
    edge_data = G_modified.get_edge_data(u, v)
    
    for data in edge_data.values():
        if "geometry" in data:
            # Se tiver geometria, usa a forma real da rua
            route_lines.extend([(lat, lon) for lon, lat in data["geometry"].coords])
        else:
            # Caso contrário, faz uma linha reta entre os pontos
            route_lines.append((G.nodes[u]["y"], G.nodes[u]["x"]))
            route_lines.append((G.nodes[v]["y"], G.nodes[v]["x"]))

folium.PolyLine(
    route_lines, color="blue", weight=5, opacity=0.7, popup="Rota"
).add_to(m)

# Exibir o mapa interativo
m.save("mapa_interativo.html")
m
