import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

# Função heurística para o A* (distância geodésica entre dois nós)
def heuristic(node1, node2, graph):
    coord1 = (graph.nodes[node1]["y"], graph.nodes[node1]["x"])
    coord2 = (graph.nodes[node2]["y"], graph.nodes[node2]["x"])
    return geodesic(coord1, coord2).meters

def RotaAStar(graph, origin_point, destination_point):
    # Encontrar os nós mais próximos no grafo modificado
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    # Criar uma versão da função heurística que sempre passa o grafo
    def heuristic_with_graph(n1, n2):
        return heuristic(n1, n2, graph)

    # Encontrar a rota mais curta usando o A*
    route = nx.astar_path(graph, orig_node, dest_node, heuristic=heuristic_with_graph, weight="length")

    return route
