import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic

# Configurações iniciais
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros
graph = ox.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Área a ser evitada
avoid_location = (-23.72456530977091, -46.574473368105146)  # Coordenadas do ponto central da área a evitar
avoid_radius = 0  # Raio da área a ser evitada, em metros

# Ajustar pesos das arestas na área a ser evitada
avoid_point = Point(avoid_location[1], avoid_location[0])
G_modified = graph.copy()

for u, v, k, data in G_modified.edges(data=True, keys=True):  # Inclui 'keys' para suportar MultiDiGraph
    u_point = Point(graph.nodes[u]["x"], graph.nodes[u]["y"])
    v_point = Point(graph.nodes[v]["x"], graph.nodes[v]["y"])
    # Verifica se a aresta cruza a área a ser evitada
    if u_point.distance(avoid_point) < avoid_radius / 1000 or v_point.distance(avoid_point) < avoid_radius / 1000:
        data["length"] *= 10  # Aumenta o peso da aresta

# Função heurística para o A* (distância geodésica entre dois nós)
def heuristic(node1, node2):
    coord1 = (graph.nodes[node1]["y"], graph.nodes[node1]["x"])
    coord2 = (graph.nodes[node2]["y"], graph.nodes[node2]["x"])
    return geodesic(coord1, coord2).meters

# Definir origem e destino
origin_point = (-23.72414295696128, -46.57761691709549)
destination_point = (-23.725213569653757, -46.56954883239719)

# Encontrar os nós mais próximos no grafo modificado
orig_node = ox.distance.nearest_nodes(G_modified, origin_point[1], origin_point[0])
dest_node = ox.distance.nearest_nodes(G_modified, destination_point[1], destination_point[0])

# Verificar se os nós estão corretos
print(f"Nó de origem: {orig_node}, Nó de destino: {dest_node}")

# Encontrar a rota mais curta usando o A*
try:
    route = nx.astar_path(G_modified, orig_node, dest_node, heuristic=heuristic, weight="length")
    print("Rota encontrada:", route)
except nx.NetworkXNoPath:
    print("Erro: Nenhum caminho encontrado entre os nós!")
    route = None

if route:
    # Converter o grafo para GeoDataFrame
    edges = ox.graph_to_gdfs(graph, nodes=False)

    # Criar lista de pares de nós para a rota
    route_pairs = list(zip(route[:-1], route[1:]))

    # Adaptar filtragem para índices de três elementos (u, v, key)
    route_edges = edges.loc[edges.index.map(lambda x: (x[0], x[1]) in route_pairs)]

    # Verificar se a rota foi gerada corretamente
    if route_edges.empty:
        print("Erro: A rota não foi encontrada no GeoDataFrame!")
    else:
        # Salvar como arquivo KML
        route_edges.to_file("rota.kml", driver="KML")
        print("Arquivo KML salvo como 'rota.kml'")

ox.plot_graph(G_modified)