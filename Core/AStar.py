import osmnx as ox
import networkx as nx
import math
import time
import numpy as np

# Função para calcular o peso personalizado considerando distância, perigo e componentes NMF por período
def custom_weight(graph, periodo):
    alpha = 1  # Fator para a distância
    beta = 10   # Fator para o perigo (ajuste conforme necessário)

    # Ajuste do índice de período
    periodo_index = {"manha": 0, "tarde": 1, "noite": 2}
    periodo_idx = periodo_index.get(periodo, 0)  # Default é manhã

    for u, v, data in graph.edges(data=True):
        # Obtém a distância da aresta
        distance = data.get("length", 1)  # Usa 1 como fallback se a distância não estiver disponível

        # Ajusta os valores de perigo com base nos componentes NMF para o período específico
        crime = float(data.get(f"nmf_component_{periodo_idx + 1}", 0))  # Garantir que seja numérico
        
        # Calcula o perigo total como o componente NMF específico para o período
        penalty = crime
        
        # Calcula o peso da aresta, combinando distância e perigo
        data['weight'] = alpha * distance + beta * penalty

    return graph

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
def RotaAStar(graph, origin_point, destination_point, periodo, parameter):
    # Encontrar os nós mais próximos no grafo
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    # Ajustar os pesos do grafo considerando os componentes NMF para o período específico
    graph = custom_weight(graph, periodo)

    start_time = time.time()
    # Encontrar a rota mais curta usando A* com a heurística personalizada e pesos ajustados
    route = nx.astar_path(graph, orig_node, dest_node, weight=parameter, heuristic=lambda u, v: heuristic(u, v, graph, periodo))
    end_time = time.time()
    print("Tempo de execução do A*: ", end_time - start_time)

    return route
