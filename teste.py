import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from tqdm import tqdm
import math


# _____Configurações iniciais_____
Fei_Location = (-23.72403491298448, -46.579397903870166)
graph_radio = 2000

# Gerar o grafo a partir da localização central
Graph = ox.graph.graph_from_point(Fei_Location, dist=graph_radio, network_type="drive")

# Plotar ruas com pesos
for u, v, k, data in Graph.edges(keys=True, data=True):
    data["teste"] = 1
    data["sla"] = 1
    break

for u, v, k, data in Graph.edges(keys=True, data=True):
    print(data)
    break