from MapFunctions import haversine
import pandas as pd
import os
import osmnx as ox
from tqdm import tqdm
import matplotlib.pyplot as plt



# _____Extraindo Regiões Perigosas_____
def CrimeLocations(pasta):

    # Extrair arquivos na pasta
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    Locations = [[],[]]

    # Ler os arquivos CSV
    for arquivo in tqdm(arquivos, desc="Lendo arquivos de BOs"):
        if not arquivo.endswith(".csv"):
            continue
        # Ler o arquivo CSV
        df = pd.read_csv(pasta + arquivo, low_memory=False)

    # Remover valores inválidos e garantir que latitude e longitude estejam alinhadas
        # Remove valores que não são floats
        df["latitude"] = df["latitude"].apply(lambda x: x if isinstance(x, float) else None)
        df["longitude"] = df["longitude"].apply(lambda x: x if isinstance(x, float) else None)

        # Remover valores nulos
        df = df[["latitude", "longitude"]].dropna().astype(float)
        df = df[(df["latitude"] != 0.0) & (df["longitude"] != 0.0)]

        # Adicionar os valores às listas correspondentes
        Locations[0].extend(df["latitude"].tolist())
        Locations[1].extend(df["longitude"].tolist())

    # Gerar erro se tamanhos diferentes 
    if len(Locations[0]) != len(Locations[1]):
        print("Erro: Quantidade de Valores Diferentes")
        exit()

    return Locations

# _____ Filtro de Crimes dentro de um raio _____
def FilterCrimes(Graph_Location, Graph_radio, CrimeLocations):
    FilteredLocations = [[],[]]
    for i in range(len(CrimeLocations[0])):
        if haversine(Graph_Location[0], Graph_Location[1], CrimeLocations[0][i], CrimeLocations[1][i]) <= Graph_radio:
            FilteredLocations[0].append(CrimeLocations[0][i])
            FilteredLocations[1].append(CrimeLocations[1][i])
    return FilteredLocations

# _____ Aplicação de Crimes ao Grafo _____
def CrimeAplication(Graph, CrimeLocations):

    # Inicializar pesos das ruas
    for u, v, k, data in Graph.edges(keys=True, data=True):
        data['danger'] = 1

    # Usar osmnx para encontrar o nó mais próximo para cada ponto
    for i in tqdm(range(len(CrimeLocations[0])), desc="Determinando Pesos das Ruas"):
        lat = CrimeLocations[0][i]
        lon = CrimeLocations[1][i]

        nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
        for u, v, k, data in Graph.edges(keys=True, data=True):
            if u == nearest_node or v == nearest_node:
                data['danger'] += 1
                break

    for __, __, __, data in Graph.edges(keys=True, data=True):
        if data['danger'] < 10:
            data['danger'] = 1

    # Conferindo se os pesos estao corretos
    # for __, __, __, data in Graph.edges(keys=True, data=True):
    #     if data['danger'] > 10:
    #         print("MAIOR:", data['danger'])
    #     else:
    #         print("MENOR:", data['danger'])

    return Graph

def CrimeColorsPlot(Graph):
    # Obter o comprimento máximo para normalização
    max_length = max([data['danger'] for u, v, k, data in Graph.edges(keys=True, data=True)])


    # _____Atribuir cores e plotar o gráfico_____
    fig, ax = ox.plot_graph(Graph, show=False, close=False)

    # Definir uma paleta de cores personalizada para o gráfico
    cmap = plt.cm.get_cmap('RdYlGn_r')  # Vermelho para laranja/verde para azul (inverso de 'RdYlGn')

    # Plotar ruas com pesos
    for u, v, k, data in Graph.edges(keys=True, data=True):       
            length = data['danger']

            # # Verifique se a chave 'geometry' existe antes de acessar
            # if 'geometry' in data:
            #     line = data['geometry']
            #     # Normalizar o peso para usar com a paleta de cores
            #     color = cmap(length / max_length)  # Cor proporcional ao peso
            #     ax.plot(*line.xy, color=color, linewidth=2)

            # Verifique se a chave 'geometry' existe antes de acessar
            if 'geometry' in data:
                if data['danger'] > 10:
                    line = data['geometry']
                    # Normalizar o peso para usar com a paleta de cores
                    color = cmap(length / max_length)  # Cor proporcional ao peso
                    ax.plot(*line.xy, color=color, linewidth=2)

    return fig, ax

def GraphConversionToHotSpots(Graph):
    HotSpots = []
    for u, v, k, data in Graph.edges(keys=True, data=True):
        if data['danger'] > 10:
            mid_lat = (Graph.nodes[u]['y'] + Graph.nodes[v]['y']) / 2
            mid_lon = (Graph.nodes[u]['x'] + Graph.nodes[v]['x']) / 2
            HotSpots.append((mid_lat, mid_lon))
    return HotSpots
