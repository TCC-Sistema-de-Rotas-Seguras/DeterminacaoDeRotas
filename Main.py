import Crimes
import osmnx as ox
from MapFunctions import get_geolocation, RoutePlot, FoliumMap
from AStar import RotaAStar
from Djikstra import RotaDijkstra
import matplotlib.pyplot as plt

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.683179061843447, -46.59369201082801)
Graph_radio = 10000
BOs_folder = "./Data/Bos"
Graph_filename = "Graph.graphml"
Origin_address = "Centro Universitário FEI, São Bernardo do Campo, Brasil"
Destination_address = "Supermercado Coop, São Bernardo do Campo, Brasil"



# ____ Localização de Origem e Destino ____
# Origin_point = get_geolocation(Origin_address)
# Destination_point = get_geolocation(Destination_address)
Origin_point = (-23.64929717646927, -46.62064284683985)
Destination_point = (-23.72491009234944, -46.57738418012019)


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

# ____ Follium Map ____
map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar)
map.save("Mapa.html")
    
plt.title("Rota com A*")
plt.show()


# ____ Plotar Rota com Djikstra ____
fig, ax = Crimes.CrimeColorsPlot(Graph)
RoutePlot(ax, Graph, Route_Djikstra)

plt.title("Rota com Djikstra")
plt.show()

map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_Djikstra)
map.save("Mapa.html")