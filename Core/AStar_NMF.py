import osmnx as ox
import networkx as nx
import math
import numpy as np

# Função heurística para o algoritmo A* considerando os componentes do NMF na penalização
def heuristic(node, target, graph, periodo):
    # Obtém coordenadas dos nós
    x1, y1 = graph.nodes[node]['x'], graph.nodes[node]['y']
    x2, y2 = graph.nodes[target]['x'], graph.nodes[target]['y']

    # Distância euclidiana
    euclidean_distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # Ajuste do índice de período
    periodo_index = {"manha": 0, "tarde": 1, "noite": 2}
    periodo_idx = periodo_index.get(periodo, 0)  # Default é manhã
    
    # Perigo médio estimado com base no componente NMF específico para o período
    avg_danger = sum(np.mean([float(data.get(f"nmf_component_{periodo_idx + 1}", 0))])
                     for _, _, data in graph.edges(node, data=True)) / max(1, len(graph.edges(node)))

    # Combinação de distância e perigo na heurística
    return euclidean_distance + (avg_danger * euclidean_distance)

# Função para encontrar a rota usando A* com heurística e componentes NMF para o período
def RotaAStar_NMF(graph, origin_point, destination_point, periodo, parameter):
    # Encontrar os nós mais próximos no grafo
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    route = nx.astar_path(graph, orig_node, dest_node, weight=parameter, heuristic=lambda u, v: heuristic(u, v, graph, periodo))


    return route
