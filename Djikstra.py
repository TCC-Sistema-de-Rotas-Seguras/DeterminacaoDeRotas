import osmnx as ox
import networkx as nx
import time

# Função para calcular o peso personalizado considerando distância e perigo
def custom_weight(graph):
    alpha = 1  # Fator para a distância
    beta = 1   # Fator para o perigo (ajuste conforme necessário)

    for u, v, data in graph.edges(data=True):
        # Obtém a distância da aresta
        distance = data.get("length", 1)  # Usa 1 como fallback se a distância não estiver disponível
        danger = data.get("danger", 0)  # Assume perigo 0 caso não esteja definido

        # Peso baseado na soma da distância e do perigo
        data['weight'] = alpha * distance + beta * danger

    return graph

# Função para encontrar a rota usando Dijkstra
def RotaDijkstra(graph, origin_point, destination_point):
    # Encontrar os nós mais próximos no grafo
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    # Ajustar os pesos do grafo
    graph = custom_weight(graph)

    start_time = time.time()
    # Encontrar a rota mais curta usando Dijkstra
    route = nx.shortest_path(graph, orig_node, dest_node, weight='weight', method="dijkstra")
    end_time = time.time()
    print("Tempo de execução do Dijkstra: ", end_time - start_time)

    return route
