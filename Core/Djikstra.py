import osmnx as ox
import networkx as nx
import time

# Função para encontrar a rota usando Dijkstra
def RotaDijkstra(graph, origin_point, destination_point, parameter):
    # Encontrar os nós mais próximos no grafo
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    start_time = time.time()
    # Encontrar a rota mais curta usando Dijkstra
    route = nx.shortest_path(graph, orig_node, dest_node, weight=parameter, method="dijkstra")
    end_time = time.time()
    print("Tempo de execução do Dijkstra: ", end_time - start_time)

    return route
