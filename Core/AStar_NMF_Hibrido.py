import osmnx as ox
import networkx as nx
import math
import numpy as np

def preparar_coords(graph):
    return {node: (data['x'], data['y']) for node, data in graph.nodes(data=True)}

def heuristic_hibrida(u, v, graph, coords, periodo_idx):
    x1, y1 = coords[u]
    x2, y2 = coords[v]

    euclidean_distance = math.hypot(x1 - x2, y1 - y2)

    perigos = [float(data.get(f"nmf_component_{periodo_idx + 1}", 0)) for _, _, data in graph.edges(u, data=True)]
    avg_danger = np.mean(perigos) if perigos else 0

    return euclidean_distance + (avg_danger * euclidean_distance)

def RotaAStar_NMF_Hibrida(graph, origin_point, destination_point, periodo, parameter):
    orig_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
    dest_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

    periodo_index = {"manha": 0, "tarde": 1, "noite": 2}
    periodo_idx = periodo_index.get(periodo, 0)

    coords = preparar_coords(graph)

    route = nx.astar_path(
        graph,
        orig_node,
        dest_node,
        weight=parameter,
        heuristic=lambda u, v: heuristic_hibrida(u, v, graph, coords, periodo_idx)
    )

    return route

