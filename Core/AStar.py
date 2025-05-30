import osmnx as ox
import networkx as nx
import math
import time

# Função heurística para o algoritmo A*
def heuristic(node, target, graph):
    # Obtém coordenadas dos nós
    x1, y1 = graph.nodes[node]['x'], graph.nodes[node]['y']
    x2, y2 = graph.nodes[target]['x'], graph.nodes[target]['y']

    # Distância euclidiana
    euclidean_distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # Perigo médio estimado
    avg_danger = sum(float(data.get("danger", 0)) for _, _, data in graph.edges(node, data=True)) / max(1, len(graph.edges(node)))

    # Combinação de distância e perigo na heurística
    return euclidean_distance + (avg_danger * euclidean_distance)

# Função para encontrar a rota usando A* com heurística
def RotaAStar(graph, origin_point, destination_point, parameter):
    # Encontrar os nós mais próximos no grafo
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    start_time = time.time()
    # Encontrar a rota mais curta usando A* com heurística
    route = nx.astar_path(graph, orig_node, dest_node, weight=parameter, heuristic=lambda u, v: heuristic(u, v, graph))
    end_time = time.time()

    return route