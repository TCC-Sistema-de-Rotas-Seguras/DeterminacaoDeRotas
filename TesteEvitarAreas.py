import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# Configurações iniciais
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros
ox.settings.bidirectional_network_types += "drive"
G = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Área a ser evitada
avoid_location = (-23.72456530977091, -46.574473368105146)  # Coordenadas do ponto central da área a evitar
avoid_radius = 0  # Raio da área a ser evitada, em metros

# Visualizar o grafo original
fig, ax = plt.subplots(1, 2, figsize=(15, 7))  # 1 linha, 2 colunas

# Plotar o grafo original no primeiro subplot
ox.plot_graph(G, ax=ax[0], show=False, close=False)
ax[0].set_title("Grafo Original")

# Identificar os nós dentro da área a ser evitada
nodes_to_avoid = []
for node, data in G.nodes(data=True):
    node_point = Point(data["x"], data["y"])  # Cria um ponto com as coordenadas do nó
    avoid_point = Point(avoid_location[1], avoid_location[0])  # Ponto da área evitada
    # Distância entre o nó e o ponto da área evitada
    if node_point.distance(avoid_point) < avoid_radius / 1000:  # Convertendo metros para km
        nodes_to_avoid.append(node)

# Criar uma cópia do grafo sem os nós a serem evitados
G_modified = G.copy()
G_modified.remove_nodes_from(nodes_to_avoid)

# Plotar o grafo modificado no segundo subplot
ox.plot_graph(G_modified, ax=ax[1], show=False, close=False)
ax[1].set_title("Grafo Após Remover Área Evitada")

# Mostrar ambos os gráficos
plt.tight_layout()  # Ajusta o espaçamento entre os subgráficos
plt.show()

# Definir origem e destino
origin_point = (-23.72414295696128, -46.57761691709549)
destination_point = (-23.725213569653757, -46.56954883239719)

# Encontrar os nós mais próximos no grafo modificado
orig_node = ox.distance.nearest_nodes(G_modified, origin_point[1], origin_point[0])
dest_node = ox.distance.nearest_nodes(G_modified, destination_point[1], destination_point[0])

# Encontrar a rota mais curta no grafo modificado (Utilizando Djikstra)
# Link Documentação: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.shortest_path.html#networkx.algorithms.shortest_paths.generic.shortest_path
route = ox.shortest_path(G_modified, orig_node, dest_node, weight="length")

# Plotar a rota com a área evitada no grafo modificado
fig, ax = ox.plot_graph_route(G_modified, route, show=False, close=False)

# Adicionar a área evitada no gráfico (círculo)
avoid_point = Point(avoid_location[1], avoid_location[0])
circle = Circle((avoid_point.x, avoid_point.y), avoid_radius / 1000, color='red', alpha=0.3, label='Área Evitada')
ax.add_patch(circle)

# Mostrar o gráfico com a área evitada
plt.legend()
plt.show()
