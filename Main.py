import Crimes
import os
import osmnx as ox
from MapFunctions import get_geolocation, RoutePlot, FoliumMap
from AStar import RotaAStar
from Djikstra import RotaDijkstra
import matplotlib.pyplot as plt

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.724249554085418, -46.57659561047842)
Graph_radio = 10000
BOs_folder = "./Data/Bos/"
Graph_folder = "./Data/Graphs/"
Graph_filename = "Merged_Graph.graphml"

# ____ Localização de Origem e Destino ____
Origin_point = (-23.756913989254592, -46.60476953391852)
Destination_point = (-23.739040899185984, -46.55052453900106)


if Origin_point is None or Destination_point is None:
    print("Erro: Endereço Inválido")
    exit()

if not os.path.exists("Data"):
    os.makedirs("Data") 
if not os.path.exists("Data/Graphs"):
    os.makedirs("Data/Graphs")
if not os.path.exists("Data/Bos"):
    os.makedirs("Data/Bos")


if not os.path.exists(Graph_folder + Graph_filename):
    # ____ Localização de Crimes____
    Locations = Crimes.CrimeLocations(BOs_folder)
    FilteredLocations = Crimes.FilterCrimes(Graph_Location, Graph_radio, Locations)

    # ____ Geração do Grafo ____
    Graph = ox.graph.graph_from_point(Graph_Location, dist=Graph_radio, network_type="drive")

    # Aplicando peso dos crimes no grafo 
    Graph = Crimes.CrimeAplication(Graph, FilteredLocations)

    ox.save_graphml(Graph, Graph_folder + Graph_filename)
else:
    Graph = ox.load_graphml(Graph_folder + Graph_filename)

# ____ Determinação de Rota ____
Route_AStar = RotaAStar(Graph, Origin_point, Destination_point)
Route_Djikstra = RotaDijkstra(Graph, Origin_point, Destination_point)

# ____ Plotar Grafo ____
fig, ax = Crimes.CrimeColorsPlot(Graph)

# ____ Plotar Rota ____
RoutePlot(ax, Graph, Route_AStar)

# _____ Determinar Hotspots _____
Hotspots = Crimes.GraphConversionToHotSpots(Graph)

# ____ Follium Map ____
map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar, Hotspots)
    
plt.title("Rota com A*")
plt.show()


# # ____ Plotar Rota com Djikstra ____
# fig, ax = Crimes.CrimeColorsPlot(Graph)
# RoutePlot(ax, Graph, Route_Djikstra)

# plt.title("Rota com Djikstra")
# plt.show()

# map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_Djikstra)
# map.save("Mapa.html")