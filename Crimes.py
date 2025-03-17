import pandas as pd
from datetime import datetime
import os
import osmnx as ox
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
from haversine import haversine

# Função para classificar os crimes por período do dia
def classify_crimes_by_time(df):
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

# Função para processar arquivos CSV de boletins de ocorrência
def CrimeLocations(pasta):
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    Locations = [[], [], []]  # Adicionando lista extra para períodos do dia
    crimes_by_period = {"manha": 0, "tarde": 0, "noite": 0}

    for arquivo in arquivos:
        if not arquivo.endswith(".csv"):
            continue

        df = pd.read_csv(pasta + arquivo, low_memory=False)  # Evitar avisos de tipo misto

        # Garantir que as colunas necessárias existam antes de processar
        if not all(col in df.columns for col in ["latitude", "longitude", "hora_ocorrencia_bo"]):
            print(f"Aviso: Arquivo {arquivo} não contém as colunas esperadas.")
            continue

        # Corrigir valores inválidos em latitude e longitude
        df["latitude"] = pd.to_numeric(df["latitude"], errors='coerce')
        df["longitude"] = pd.to_numeric(df["longitude"], errors='coerce')

        df = df.dropna(subset=["latitude", "longitude"])
        df = df[(df["latitude"] != 0.0) & (df["longitude"] != 0.0)]

        # Classificar os crimes por período do dia
        df = classify_crimes_by_time(df)

        # Contagem de crimes por período
        for period in ['manha', 'tarde', 'noite']:
            crimes_by_period[period] += df[df['periodo'] == period].shape[0]

        # Adicionar dados a Locations
        Locations[0].extend(df["latitude"].tolist())
        Locations[1].extend(df["longitude"].tolist())
        Locations[2].extend(df["periodo"].tolist())  # Adicionando período correspondente

    if len(Locations[0]) != len(Locations[1]) or len(Locations[0]) != len(Locations[2]):
        print("Erro: Quantidade de valores diferentes em Locations.")
        exit()

    return Locations, crimes_by_period

# Filtragem de crimes dentro de um raio do ponto central
def FilterCrimes(Graph_Location, Graph_radio, CrimeLocations):
    FilteredLocations = [[], [], []]
    for i in range(len(CrimeLocations[0])):
        if haversine(Graph_Location, (CrimeLocations[0][i], CrimeLocations[1][i])) <= Graph_radio:
            FilteredLocations[0].append(CrimeLocations[0][i])
            FilteredLocations[1].append(CrimeLocations[1][i])
            FilteredLocations[2].append(CrimeLocations[2][i])  # Adicionar período correspondente
    return FilteredLocations

# Aplicação de crimes no grafo (pesos nas ruas)
def CrimeAplication(Graph, CrimeLocations, crimes_by_period):
    for u, v, k, data in Graph.edges(keys=True, data=True):
        data.setdefault('danger', 1)
        data.setdefault('manha', 0)
        data.setdefault('tarde', 0)
        data.setdefault('noite', 0)
        data['street_name'] = data.get('name', f"Rua {u}-{v}")

    for i in tqdm(range(len(CrimeLocations[0])), desc="Determinando Pesos das Ruas"):
        lat = CrimeLocations[0][i]
        lon = CrimeLocations[1][i]
        crime_period = CrimeLocations[2][i]

        nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
        for u, v, k, data in Graph.edges(keys=True, data=True):
            if u == nearest_node or v == nearest_node:
                data['danger'] += 1
                data[crime_period] += 1  # Atualiza o contador de crimes por período
                break

    return Graph

# Gerar mapa de cores de crimes no grafo
def CrimeColorsPlot(Graph):
    max_length = max([data['danger'] for u, v, k, data in Graph.edges(keys=True, data=True)])

    fig, ax = ox.plot_graph(Graph, show=False, close=False)
    cmap = plt.cm.get_cmap('RdYlGn_r')

    for u, v, k, data in Graph.edges(keys=True, data=True):       
        length = data['danger']
        if 'geometry' in data and data['danger'] > 10:
            line = data['geometry']
            color = cmap(length / max_length)
            ax.plot(*line.xy, color=color, linewidth=2)

    return fig, ax

# Converter Grafo para HotSpots
def GraphConversionToHotSpots(Graph):
    HotSpots = []
    for u, v, k, data in Graph.edges(keys=True, data=True):
        if data['danger'] > 10:
            mid_lat = (Graph.nodes[u]['y'] + Graph.nodes[v]['y']) / 2
            mid_lon = (Graph.nodes[u]['x'] + Graph.nodes[v]['x']) / 2
            HotSpots.append((mid_lat, mid_lon))
    return HotSpots
