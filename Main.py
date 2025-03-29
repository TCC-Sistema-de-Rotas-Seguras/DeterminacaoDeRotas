from Core.Crimes import CrimeLocations, FilterCrimes, CrimeAplication, GraphConversionToHotSpots, CrimeColorsPlot
from Core.MapFunctions import get_geolocation, RoutePlot, FoliumMap
from Core.AStar import RotaAStar
from Core.Djikstra import RotaDijkstra
from Core.Nmf import main_nmf
import matplotlib.pyplot as plt
import os
import osmnx as ox

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.724222542890598, -46.57762289661209)
Graph_radio = 1000
BOs_folder = "./Data/Bos/"
Graph_folder = "./Data/Graphs/"
Graph_filename = "Graph_with_NMF.graphml"

# ____ Localização de Origem e Destino ____
Origin_point = (-23.721843100582227, -46.57406092319069)
Destination_point = (-23.72194132403423, -46.58071280114315)


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
    Locations, crimes_by_period = CrimeLocations(BOs_folder)
    FilteredLocations = FilterCrimes(Graph_Location, Graph_radio, Locations)

    # ____ Geração do Grafo ____
    Graph = ox.graph.graph_from_point(Graph_Location, dist=Graph_radio, network_type="drive")

    # Aplicando peso dos crimes no grafo 
    Graph = CrimeAplication(Graph, FilteredLocations, crimes_by_period)

    ox.save_graphml(Graph, Graph_folder + Graph_filename)
else:
    Graph = ox.load_graphml(Graph_folder + Graph_filename)

# Chamando o NMF para extrair a matriz de crimes e aplicar NMF
Graph, ruas, crime_matrix, W, H = main_nmf(Graph_folder + Graph_filename)

# ____ Determinação de Rota ____
Route_AStar_comCrimes = RotaAStar(Graph, Origin_point, Destination_point, "weight")
# Route_AStar_semCrimes  = RotaAStar(Graph, Origin_point, Destination_point, "lenght")
# Route_Djikstra = RotaDijkstra(Graph, Origin_point, Destination_point)

# ____ Plotar Grafo ____
fig, ax = CrimeColorsPlot(Graph)

# ____ Plotar Rota ____
RoutePlot(ax, Graph, Route_AStar_comCrimes)

# _____ Determinar Hotspots _____
Hotspots = GraphConversionToHotSpots(Graph)

# ____ Follium Map ____
map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar_comCrimes)
# map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar_semCrimes)
    
plt.title("Rota com A*")
plt.show()


# # ____ Plotar Rota com Djikstra ____
# fig, ax = Crimes.CrimeColorsPlot(Graph)
# RoutePlot(ax, Graph, Route_Djikstra)

# plt.title("Rota com Djikstra")
# plt.show()

# map = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_Djikstra)
# map.save("Mapa.html")