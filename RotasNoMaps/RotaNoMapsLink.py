import osmnx as ox
import networkx as nx

# Localização inicial e configuração do grafo
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros
graph = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Origem e destino
origin_point = (-23.72414295696128, -46.57761691709549)
destination_point = (-23.725213569653757, -46.56954883239719)

# Encontrar os nós mais próximos no grafo
orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

# Encontrar a rota mais curta
route = nx.shortest_path(graph, orig_node, dest_node, weight="length")

# Obter coordenadas dos nós na rota
route_coords = [(graph.nodes[node]["y"], graph.nodes[node]["x"]) for node in route]

# Gerar string para a URL do Google Maps
waypoints = "|".join([f"{lat},{lon}" for lat, lon in route_coords])

# Criar URL para visualizar no Google Maps
maps_url = f"https://www.google.com/maps/dir/?api=1&origin={route_coords[0][0]},{route_coords[0][1]}&destination={route_coords[-1][0]},{route_coords[-1][1]}&travelmode=driving&waypoints={waypoints}"
print("Abra o link abaixo para visualizar a rota no Google Maps:")
print(maps_url)
