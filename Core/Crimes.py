from Core.MapFunctions import haversine
import pandas as pd
import os
import osmnx as ox
from tqdm import tqdm
import matplotlib.pyplot as plt

# Função para classificar os crimes por período do dia
def CrimesByTime(df):
    def get_period(hour):
        if 6 <= hour < 12:
            return 'manha'
        elif 12 <= hour < 18:
            return 'tarde'
        else:
            return 'noite'

    # Convertendo 'hora_ocorrencia_bo' para datetime e extraindo a hora
    df['hora_ocorrencia'] = pd.to_datetime(df['hora_ocorrencia_bo'], format='%H:%M:%S', errors='coerce').dt.hour
    df['periodo'] = df['hora_ocorrencia'].apply(get_period)
    
    return df

# _____Extraindo Regiões Perigosas_____
def CrimeLocations(pasta):

    # Extrair arquivos na pasta
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    Locations = [[],[], []]  # Lista para latitudes, longitudes e períodos
    crimes_by_period = {"manha": 0, "tarde": 0, "noite": 0}

    # Ler os arquivos CSV
    for arquivo in tqdm(arquivos, desc="Lendo arquivos CSV"):
        if not arquivo.endswith(".csv"):
            continue
        # Ler o arquivo CSV
        df = pd.read_csv(pasta + arquivo, low_memory=False)
        df.columns = df.columns.str.strip().str.lower()  # Remover espaços extras e converter para minúsculas
        
        if 'hora_ocorrencia_bo' not in df.columns:
            print(f"Erro: Coluna 'hora_ocorrencia_bo' não encontrada no arquivo {arquivo}.")
            print(f"Colunas disponíveis: {df.columns.tolist()}")
            continue

        # Remover valores inválidos e garantir que latitude e longitude estejam alinhadas
        df["latitude"] = df["latitude"].apply(lambda x: x if isinstance(x, float) else None)
        df["longitude"] = df["longitude"].apply(lambda x: x if isinstance(x, float) else None)

        # Remover valores nulos
        df = df[["latitude", "longitude", "hora_ocorrencia_bo"]].dropna().astype({"latitude": float, "longitude": float})
        df = df[(df["latitude"] != 0.0) & (df["longitude"] != 0.0)]
 
        # Classificar os crimes por período do dia
        df = CrimesByTime(df)

        # Contagem de crimes por período
        for period in ['manha', 'tarde', 'noite']:
            crimes_by_period[period] += df[df['periodo'] == period].shape[0]

        # Adicionar os valores às listas correspondentes
        Locations[0].extend(df["latitude"].tolist())  # Latitudes
        Locations[1].extend(df["longitude"].tolist())  # Longitudes
        Locations[2].extend(df["periodo"].tolist())  # Períodos

    # Garantir que todas as listas tenham o mesmo tamanho
    if len(Locations[0]) != len(Locations[1]) or len(Locations[0]) != len(Locations[2]):
        print("Erro: Quantidade de Valores Diferentes nas listas.")
        exit()

    return Locations

# _____ Filtro de Crimes dentro de um raio _____
def FilterCrimes(Graph_Location, Graph_radio, CrimeLocations):
    FilteredLocations = [[],[],[]]
    for i in range(len(CrimeLocations[0])):
        if haversine(Graph_Location[0], Graph_Location[1], CrimeLocations[0][i], CrimeLocations[1][i]) <= Graph_radio:
            FilteredLocations[0].append(CrimeLocations[0][i])
            FilteredLocations[1].append(CrimeLocations[1][i])
            FilteredLocations[2].append(CrimeLocations[2][i])
    return FilteredLocations

# _____ Aplicação de Crimes ao Grafo _____
def CrimeAplication(Graph, Locations):

    # Inicializar pesos das ruas
    for u, v, k, data in Graph.edges(keys=True, data=True):
        data['danger'] = 1
        data.setdefault('danger_manha', 0)
        data.setdefault('danger_tarde', 0)
        data.setdefault('danger_noite', 0)
        data['street_name'] = data.get('name', f"Rua {u}-{v}")

    # Usar osmnx para encontrar o nó mais próximo para cada ponto
    for i in tqdm(range(len(Locations[0])), desc="Determining Street Weights"):
        lat = Locations[0][i]  # Latitude
        lon = Locations[1][i]  # Longitude
        crime_period = 'danger_' + Locations[2][i]  # Período (manha, tarde, noite)

        nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
        for u, v, k, data in Graph.edges(keys=True, data=True):
            if u == nearest_node or v == nearest_node:
                data['danger'] += 1
                data[crime_period] += 1
                break

    #for __, __, __, data in Graph.edges(keys=True, data=True):
    #    if data['danger'] < 10:
    #        data['danger'] = 1

    return Graph

def CrimeColorsPlot(Graph):
    # Garantir que 'danger' é numérico antes de calcular o máximo
    max_length = max([float(data['danger']) if isinstance(data['danger'], (int, float)) else 0
                      for u, v, k, data in Graph.edges(keys=True, data=True)])

    fig, ax = ox.plot_graph(Graph, show=False, close=False)
    cmap = plt.cm.get_cmap('RdYlGn_r')

    for u, v, k, data in Graph.edges(keys=True, data=True):
        # Garantir que 'danger' seja um número antes da comparação
        try:
            length = float(data['danger'])  # Tenta converter para float
        except ValueError:
            length = 0  # Caso não seja possível, define como 0

        if 'geometry' in data and length > 10:  # Compara o valor convertido
            line = data['geometry']
            if max_length > 0:  # Previne divisão por zero
                color = cmap(length / max_length)
            else:
                color = cmap(0)  # Caso max_length seja zero, atribui a cor mínima
            ax.plot(*line.xy, color=color, linewidth=2)

    return fig, ax


def GraphConversionToHotSpots(Graph):
    HotSpots = []
    for u, v, k, data in Graph.edges(keys=True, data=True):
        try:
            danger_value = float(data['danger'])  # Tenta converter para float
        except ValueError:
            danger_value = 0  # Caso não seja possível, define como 0

        if danger_value > 10:  # Compara o valor convertido
            mid_lat = (Graph.nodes[u]['y'] + Graph.nodes[v]['y']) / 2
            mid_lon = (Graph.nodes[u]['x'] + Graph.nodes[v]['x']) / 2
            HotSpots.append((mid_lat, mid_lon))
    
    return HotSpots

