import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from FuncoesDeterminandoAreaEvitada import Remover_Pontos_Area_Evitada, AumentarPesoAreaEvitada
from AStar import RotaAStar

# _____Configurações iniciais_____

# Localização central do mapa
Fei_Location = (-23.72403491298448, -46.579397903870166) 

# Raio do mapa em Metros
map_radio = 1609  

# dist = raio do mapa em metros
Graph = ox.graph.graph_from_point(Fei_Location, dist=map_radio, network_type="drive")

# _____Configuração Area a ser evitada_____

# (Latitude: Y, Longitude: X)
# Coordenadas do ponto central da área a evitar 
avoid_location = (-23.72456530977091, -46.574473368105146)  

# Raio da área a ser evitada (TAMANHO?)
avoid_radius = 1  

# _____Identificação de Nós a ser evitados______
Modified_Graph_PontosRemovidos = Remover_Pontos_Area_Evitada(Graph, avoid_location, avoid_radius)
Modified_Graph_PesoAumentado = AumentarPesoAreaEvitada(Graph, avoid_location, avoid_radius)

# _____Determinando Rotas_____
house_point = (-23.72414295696128, -46.57761691709549)
market_point = (-23.725213569653757, -46.56954883239719)
Route_AStar = RotaAStar(graph=Modified_Graph_PontosRemovidos, origin_point=house_point, destination_point=market_point)

# _____Plotando Mapa_____
fig, ax = ox.plot_graph_route(
    Graph,
    Route_AStar,
    route_color="blue",       # Cor da rota
    route_linewidth=3,        # Espessura da linha da rota
    show=False,
    close=False
)

# Adicionar a área evitada no gráfico (círculo)
circle = Circle((avoid_location[1], avoid_location[0]), avoid_radius / 1000, color="red", alpha=0.3, label="Área Evitada")
ax.add_patch(circle)

plt.legend()
plt.title("Rota com A*")
plt.show()

fig, ax = plt.subplots(1, 2, figsize=(15, 7))  # 1 linha, 2 colunas


# Show = False, não exibe o gráfico imediatamente
# Close = False, não fecha o gráfico após exibição impedindo novas modificações
ox.plot_graph(Modified_Graph_PontosRemovidos, ax=ax[0], show=False, close=False)
ax[0].set_title("Grafo Pontos Removidos")

ox.plot_graph(Graph, ax=ax[1], show=False, close=False)
ax[1].set_title("Grafo Original")

# Adicionando Circulo de Área Evitada
avoid_point = Point(avoid_location[1], avoid_location[0])
circle_1 = Circle((avoid_point.x, avoid_point.y), avoid_radius / 1000, color='red', alpha=0.3, label='Área Evitada')
ax[0].add_patch(circle_1)

circle_2 = Circle((avoid_point.x, avoid_point.y), avoid_radius / 1000, color='red', alpha=0.3, label='Área Evitada')
ax[1].add_patch(circle_2)

plt.show()
