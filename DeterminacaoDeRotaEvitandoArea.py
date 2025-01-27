import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# _____Configurações iniciais_____
Fei_Location = (-23.72403491298448, -46.579397903870166) # Localização central do mapa
map_radio = 1609  # Raio do mapa em Metros
Graph = ox.graph.graph_from_point(Fei_Location, dist=map_radio, network_type="drive")

# _____Configuração Area a ser evitada_____
# (Latitude: Y, Longitude: X)
avoid_location = (-23.72456530977091, -46.574473368105146)  # Coordenadas do ponto central da área a evitar 
avoid_radius = 1  # Raio da área a ser evitada (TAMANHO?)

# _____Identificação de Nós a ser evitados______
nodes_to_avoid = []

# G.nodes(data=True) - Permite a visualização dos dados dos Nós
# retorna ID_Node, {"dados do nó"}
for node, data in Graph.nodes(data=True):
    node_point = Point(data["x"], data["y"])  # Cria um ponto com as coordenadas do nó
    avoid_point = Point(avoid_location[1], avoid_location[0])  # Ponto da área evitada
    # Distância entre o nó e o ponto da área evitada
    if node_point.distance(avoid_point) < avoid_radius / 1000:  # Convertendo metros para km
        nodes_to_avoid.append(node)

# Criar uma cópia do grafo sem os nós a serem evitados
Modified_Graph = Graph.copy()
Modified_Graph.remove_nodes_from(nodes_to_avoid)

# _____Plotando Grafos_____
fig, ax = plt.subplots(1, 2, figsize=(15, 7))  # 1 linha, 2 colunas

ox.plot_graph(Graph, ax=ax[0], show=False, close=False)
ax[0].set_title("Grafo Original")

ox.plot_graph(Modified_Graph, ax=ax[1], show=False, close=False)
ax[1].set_title("Grafo Após Remover Área Evitada")

avoid_point = Point(avoid_location[1], avoid_location[0])
circle = Circle((avoid_point.x, avoid_point.y), avoid_radius / 1000, color='red', alpha=0.3, label='Área Evitada')
ax[1].add_patch(circle)

plt.show()
