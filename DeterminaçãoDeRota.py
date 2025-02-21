import Crimes
import osmnx as ox
from MapFunctions import get_geolocation, RoutePlot
from AStar import RotaAStar
import matplotlib.pyplot as plt

# ____ Variaveis Configuraveis ____
Graph_Location = (-23.72403491298448, -46.579397903870166)
Graph_radio = 2000
BOs_folder = "./Data"
Origin_address = "Centro Universitário FEI, São Bernardo do Campo, Brasil"
Destination_address = "Supermercado Coop, São Bernardo do Campo, Brasil"



# ____ Localização de Origem e Destino ____
# Origin_point = get_geolocation(Origin_address)
# Destination_point = get_geolocation(Destination_address)
Origin_point = (-23.718170875738355, -46.57389482329224)
Destination_point = (-23.72417236187511, -46.57764991589661)

print(Origin_point)
print(Destination_point)
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

# ____ Plotar Grafo ____
fig, ax = Crimes.CrimeColorsPlot(Graph)

# ____ Plotar Rota ____
# RoutePlot(ax, Graph, Route_AStar)

plt.title("Rota com A*")
plt.show()

