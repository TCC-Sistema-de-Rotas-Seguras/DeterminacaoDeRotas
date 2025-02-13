import osmnx as ox
import math

def euclidean_dist_vec(lat1, lon1, lat2, lon2):
    """Calcula a distância euclidiana entre dois pontos."""
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Criar o grafo
location = (-23.724, -46.579)
dist = 1000  # Distância em metros
G = ox.graph_from_point(location, dist=dist, network_type="drive")

# Penalizar ruas específicas com base no nome da rua
for u, v, key, data in G.edges(keys=True, data=True):
    if "Rua Exemplo" in data.get("name", ""):  # Modificar arestas de "Rua Exemplo"
        data["length"] *= 10  # Multiplica o comprimento por 10 (penalização)
        data["penalized"] = True  # Marca a aresta como penalizada

# Modificar arestas próximas a um ponto específico
avoid_point = (-23.7245, -46.578)
avoid_radius = 1  # Raio em metros
for u, v, key, data in G.edges(keys=True, data=True):
    if euclidean_dist_vec(
        G.nodes[u]["y"], G.nodes[u]["x"], avoid_point[0], avoid_point[1]
    ) < avoid_radius or euclidean_dist_vec(
        G.nodes[v]["y"], G.nodes[v]["x"], avoid_point[0], avoid_point[1]
    ) < avoid_radius:
        data["length"] *= 10  # Penalizar a aresta
        data["penalized"] = True  # Marca a aresta como penalizada

# Destacar arestas penalizadas com a cor vermelha
edge_colors = [
    "red" if data.get("penalized", False) else "black"
    for u, v, key, data in G.edges(keys=True, data=True)
]

# Visualizar o grafo com as arestas penalizadas destacadas
ox.plot_graph(G, edge_color=edge_colors, node_size=0, bgcolor="white")
