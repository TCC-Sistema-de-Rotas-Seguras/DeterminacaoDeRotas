import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from geopy.distance import geodesic

# Configurações iniciais
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros
ox.settings.bidirectional_network_types += "drive"
G = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Área a ser evitada
avoid_location = (-23.72456530977091, -46.574473368105146)  # Coordenadas do ponto central da área a evitar
avoid_radius = 0  # Raio da área a ser evitada, em metros

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

# Visualizar o grafo e a rota no mesmo gráfico
fig, ax = ox.plot_graph_route(
    G_modified,
    route,
    route_color="blue",       # Cor da rota
    route_linewidth=3,        # Espessura da linha da rota
    show=False,
    close=False
)

# Adicionar a área evitada no gráfico (círculo)
circle = Circle((avoid_point.x, avoid_point.y), avoid_radius / 1000, color="red", alpha=0.3, label="Área Evitada")
ax.add_patch(circle)

# Adicionar legendas e título
plt.legend()
plt.title("Rota com A* sobre o Grafo e Área Evitada")
plt.show()
