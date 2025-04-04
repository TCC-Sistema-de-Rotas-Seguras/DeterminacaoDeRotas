
# ____ Bibliotecas Externas ____
import matplotlib.pyplot as plt
import os
import osmnx as ox
import networkx as nx

# ____ Bibliotecas Internas ____
from Core.Crimes import CrimeLocations, FilterCrimes, CrimeAplication, CrimeColorsPlot
from Core.MapFunctions import RoutePlot, FoliumMap
from Core.AStar import RotaAStar
from Core.Djikstra import RotaDijkstra

# ___ Bibliotecas AWS ____
import io
import boto3
import tempfile
from botocore.exceptions import NoCredentialsError

# ____ Variaveis Configuraveis ____
Graph_filename = "Merged_Graph_Aplicado.graphml" # Seleciona o grafo que vai ser utilizado
Graph_AWS = "Merged_Graph_Aplicado.graphml" # Seleciona o grafo que vai ser puxado da AWS (Obs: Caso os dois forem iguais ele já baixa da AWS e usa o Grafo)

# ____ Localização de Origem e Destino ____
Origin_point = (-23.72405007639595, -46.57949541445861)
Destination_point = (-23.720464709225926, -46.5699004643136)

# ____ Geração de Repositórios ____
if not os.path.exists("Data"):
    os.makedirs("Data") 
if not os.path.exists("Data/Graphs"):
    os.makedirs("Data/Graphs")
if not os.path.exists("Data/Bos"):
    os.makedirs("Data/Bos")

BOs_folder = "./Data/Bos/"
Graph_folder = "./Data/Graphs/"

# _____________ Baixar Merged Graph da AWS ___________________
if (not os.path.exists(Graph_folder + "/" + Graph_AWS)) and Graph_filename == Graph_AWS:

    # Configuração do cliente S3
    if os.path.exists(".env"):
        s3 = boto3.client('s3')
    else:
        raise FileNotFoundError("Erro: O arquivo .env não foi encontrado. Configure o .env para baixar o Merged_Graph da AWS.")

    try:
        # Baixar o arquivo do S3 e salvar localmente
        with open("./Data/Graphs/" + Graph_AWS, "wb") as local_file:
            s3.download_fileobj('tcc-grafocriminal', Graph_AWS, local_file)

        print("Grafo baixado com sucesso!")

    except NoCredentialsError:
        print("Erro: Credenciais AWS não encontradas.")
    except Exception as e:
        print(f'Ocorreu um erro ao carregar o arquivo: {e}')
        raise

# ____ Gerar Grafo caso não exita ____

# Configuração
Graph_Location = (-23.724222542890598, -46.57762289661209)
Graph_radio = 1000

# Geração
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


# ____ Determinação de Rota ____
Route_AStar_comCrimes = RotaAStar(Graph, Origin_point, Destination_point, 2, "weight")
# Route_AStar_semCrimes  = RotaAStar(Graph, Origin_point, Destination_point, "lenght")
# Route_Djikstra = RotaDijkstra(Graph, Origin_point, Destination_point)

# ____ Plotar Grafo ____
fig, ax = CrimeColorsPlot(Graph)

# ____ Plotar Rota ____
RoutePlot(ax, Graph, Route_AStar_comCrimes)

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