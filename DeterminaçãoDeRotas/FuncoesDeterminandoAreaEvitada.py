from shapely.geometry import Point


def Remover_Pontos_Area_Evitada(Graph, avoid_location, avoid_radius):
    """
    Remove os pontos do grafo que estão dentro da área a ser evitada.

    Parâmetros
    ----------
    Graph : networkx.MultiDiGraph
        Grafo gerado pela biblioteca OSMnx.
    avoid_location : tuple
        Coordenadas do ponto central da área a ser evitada (Latitude, Longitude).
    avoid_radius : float
        Raio da área a ser evitada, em metros.

    Retorna
    -------
    Modified_Graph : networkx.MultiDiGraph
        Grafo modificado sem os pontos que estão dentro da área a ser evitada.
    """

    # Identificação de Nós a serem evitados
    nodes_to_avoid = []

    # G.nodes(data=True) - Permite a visualização dos dados dos Nós
    # retorna ID_Node, {"dados do nó"}
    for node, data in Graph.nodes(data=True):

        # Ponto do nó e ponto da área evitada
        node_point = Point(data["x"], data["y"])
        avoid_point = Point(avoid_location[1], avoid_location[0])

        # Distância entre o nó e o ponto da área evitada
        if node_point.distance(avoid_point) < avoid_radius / 1000:  # Convertendo metros para km
            nodes_to_avoid.append(node)

    # Criar uma cópia do grafo sem os nós a serem evitados
    Modified_Graph = Graph.copy()
    Modified_Graph.remove_nodes_from(nodes_to_avoid)

    return Modified_Graph

def AumentarPesoAreaEvitada(Graph, avoid_location, avoid_radius):
    """
    Aumenta o peso das arestas do grafo que cruzam a área a ser evitada.

    Parâmetros
    ----------
    Graph : networkx.MultiDiGraph
        Grafo gerado pela biblioteca OSMnx.
    avoid_location : tuple
        Coordenadas do ponto central da área a ser evitada (Latitude, Longitude).
    avoid_radius : float
        Raio da área a ser evitada, em metros.

    Retorna
    -------
    Modified_Graph : networkx.MultiDiGraph
        Grafo modificado com os pesos das arestas ajustados.
    """

    avoid_point = Point(avoid_location[1], avoid_location[0])
    G_modified = Graph.copy()

    # u - Nó 1 da aresta
    # v - Nó 2 da aresta
    # data - Dados da aresta
    for u, v, data in G_modified.edges(data=True):
        u_point = Point(G_modified.nodes[u]["y"], G_modified.nodes[u]["x"])
        v_point = Point(G_modified.nodes[v]["y"], G_modified.nodes[v]["x"])

        # Verifica se a aresta cruza a área a ser evitada
        if u_point.distance(avoid_point) < avoid_radius / 1000 or v_point.distance(avoid_point) < avoid_radius / 1000:
            print("antes:" + data["length"])
            data["length"] *= 10  # Aumenta o peso da aresta

    return G_modified

