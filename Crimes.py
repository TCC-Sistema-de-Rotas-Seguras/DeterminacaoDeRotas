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
    for arquivo in arquivos:
        if not arquivo.endswith(".csv"):
            continue
        # Ler o arquivo CSV
        df = pd.read_csv("./Data/" + arquivo)

        # Remover valores inválidos e garantir que latitude e longitude estejam alinhadas
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
        data['danger'] = 0

    # Usar osmnx para encontrar o nó mais próximo para cada ponto
    for i in tqdm(range(len(CrimeLocations[0])), desc="Determinando Pesos das Ruas"):
        lat = CrimeLocations[0][i]
        lon = CrimeLocations[1][i]

        nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
        for u, v, k, data in Graph.edges(keys=True, data=True):
            if u == nearest_node or v == nearest_node:
                data['danger'] += 1
                break

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

            # Verifique se a chave 'geometry' existe antes de acessar
            if 'geometry' in data:
                line = data['geometry']
                # Normalizar o peso para usar com a paleta de cores
                color = cmap(length / max_length)  # Cor proporcional ao peso
                ax.plot(*line.xy, color=color, linewidth=2)

    return fig, ax