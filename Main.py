import Crimes
import osmnx as ox
from MapFunctions import get_geolocation, RoutePlot, FoliumMap
from AStar import RotaAStar
from Djikstra import RotaDijkstra
import matplotlib.pyplot as plt

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.724249554085418, -46.57659561047842)
Graph_radio = 1000
BOs_folder = "./Data/Bos/"
Graph_filename = "Graph.graphml"
Origin_address = "Centro Universitário FEI, São Bernardo do Campo, Brasil"
Destination_address = "Supermercado Coop, São Bernardo do Campo, Brasil"



# ____ Localização de Origem e Destino ____
# Origin_point = get_geolocation(Origin_address)
# Destination_point = get_geolocation(Destination_address)
Origin_point = (-23.7222654611315, -46.574278181904155)
Destination_point = (-23.72442635298251, -46.5776899517496)


if Origin_point is None or Destination_point is None:
    print("Erro: Endereço Inválido")
    exit()

# ____ Localização de Crimes____
Locations = Crimes.CrimeLocations(BOs_folder)
FilteredLocations = Crimes.FilterCrimes(Graph_Location, Graph_radio, Locations)

# ____ Geração do Grafo ____
Graph = ox.graph.graph_from_point(Graph_Location, dist=Graph_radio, network_type="drive")

# Aplicando peso dos crimes no grafo 
Graph = Crimes.CrimeAplication(Graph, FilteredLocations)

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
map.save("Mapa.html")
    
plt.title("Rota com A*")
plt.show()


# # ____ Plotar Rota com Djikstra ____
# fig, ax = Crimes.CrimeColorsPlot(Graph)
# RoutePlot(ax, Graph, Route_Djikstra)

# plt.title("Rota com Djikstra")
# plt.show()

# map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_Djikstra)
# map.save("Mapa.html")