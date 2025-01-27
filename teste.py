import osmnx as ox
import matplotlib.pyplot as plt

# _____Configurações iniciais_____
Fei_Location = (-23.72403491298448, -46.579397903870166)  # Localização central do mapa
map_radio = 1609  # Raio do mapa em metros

G = ox.graph.graph_from_point(Fei_Location, dist=map_radio, network_type="drive")
print(G.nodes)