import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt

# Definir a localização e a distância
Fei_Location = (-23.72403491298448, -46.579397903870166)
one_mile = 1609  # metros

# Configurar o tipo de rede bidirecional
ox.settings.bidirectional_network_types += "drive"

# Baixar o grafo da rede viária
G = ox.graph.graph_from_point(Fei_Location, dist=one_mile, network_type="drive")

# Definir um dicionário de cores para diferentes tipos de ruas
road_colors = {
    'motorway': 'red',
    'primary': 'orange',
    'secondary': 'yellow',
    'tertiary': 'green',
    'residential': 'blue',
    'service': 'purple',
    'unclassified': 'gray'
}

# Obter as cores das arestas com base no tipo de rua (highway)
edge_colors = []
for _, _, data in G.edges(data=True):
    highway_type = data.get('highway', 'unclassified')  # 'unclassified' se não especificado
    if isinstance(highway_type, list):  # Alguns caminhos têm múltiplos tipos
        highway_type = highway_type[0]
    edge_colors.append(road_colors.get(highway_type, 'black'))  # 'black' como padrão

# Plotar o grafo com as cores das ruas
fig, ax = ox.plot.plot_graph(
    G,
    edge_color=edge_colors,
    edge_linewidth=1,
    node_size=0,
    bgcolor='white'
)

plt.show()
