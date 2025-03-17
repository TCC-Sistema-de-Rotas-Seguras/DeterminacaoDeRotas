import pandas as pd
from datetime import datetime
import os
import osmnx as ox
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
from haversine import haversine
# Função para extrair e classificar as ocorrências por período
def classify_crimes_by_time(df):
    # Função para classificar as ocorrências
    def get_period(hour):
        if 6 <= hour < 12:
            return 'manha'
        elif 12 <= hour < 18:
            return 'tarde'
        else:
            return 'noite'

    # Extraindo a hora corretamente do formato hh:mm:ss
    df['hora_ocorrencia'] = pd.to_datetime(df['hora_ocorrencia_bo'], format='%H:%M:%S', errors='coerce').dt.hour
    df['periodo'] = df['hora_ocorrencia'].apply(get_period)
    return df


def CrimeLocations(pasta):
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    Locations = [[],[]]
    crimes_by_period = {}  # Dicionário para contar crimes por período

    for arquivo in arquivos:
        if not arquivo.endswith(".csv"):
            continue
        df = pd.read_csv(pasta + arquivo)

        df["latitude"] = df["latitude"].apply(lambda x: x if isinstance(x, float) else None)
        df["longitude"] = df["longitude"].apply(lambda x: x if isinstance(x, float) else None)

        df = df[["latitude", "longitude", "hora_ocorrencia_bo"]].dropna().astype(float)
        df = df[(df["latitude"] != 0.0) & (df["longitude"] != 0.0)]

        # Classificar os crimes por período
        df = classify_crimes_by_time(df)

        # Contagem de crimes por período
        for period in ['manha', 'tarde', 'noite']:
            crimes_by_period[period] = crimes_by_period.get(period, 0) + len(df[df['periodo'] == period])

        Locations[0].extend(df["latitude"].tolist())
        Locations[1].extend(df["longitude"].tolist())

    if len(Locations[0]) != len(Locations[1]):
        print("Erro: Quantidade de Valores Diferentes")
        exit()

    return Locations, crimes_by_period

def FilterCrimes(Graph_Location, Graph_radio, CrimeLocations):
    FilteredLocations = [[],[]]
    for i in range(len(CrimeLocations[0])):
        if haversine(Graph_Location[0], Graph_Location[1], CrimeLocations[0][i], CrimeLocations[1][i]) <= Graph_radio:
            FilteredLocations[0].append(CrimeLocations[0][i])
            FilteredLocations[1].append(CrimeLocations[1][i])
    return FilteredLocations

def CrimeAplication(Graph, CrimeLocations, crimes_by_period):
    for u, v, k, data in Graph.edges(keys=True, data=True):
        data.setdefault('danger', 1)
        data.setdefault('manha', 0)
        data.setdefault('tarde', 0)
        data.setdefault('noite', 0)

    for i in tqdm(range(len(CrimeLocations[0])), desc="Determinando Pesos das Ruas"):
        lat = CrimeLocations[0][i]
        lon = CrimeLocations[1][i]

        nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
        for u, v, k, data in Graph.edges(keys=True, data=True):
            if u == nearest_node or v == nearest_node:
                data['danger'] += 1
                crime_period = CrimeLocations[2][i]  # Obtém o período da ocorrência
                if crime_period == 'manha':
                    data['manha'] += 1
                elif crime_period == 'tarde':
                    data['tarde'] += 1
                elif crime_period == 'noite':
                    data['noite'] += 1
                break

    return Graph


def generate_crime_json(Graph):
    crime_data = {}

    for u, v, k, data in Graph.edges(keys=True, data=True):
        if "geometry" in data:
            street_id = f"{u}-{v}"
            crime_data[street_id] = {
                "nome_rua": f"Rua {u}-{v}",
                "danger": data.get('danger', 1),
                "manha": data.get('manha', 0),
                "tarde": data.get('tarde', 0),
                "noite": data.get('noite', 0),
                "geometry": data["geometry"].__geo_interface__,
                "latitude": (Graph.nodes[u]['y'] + Graph.nodes[v]['y']) / 2,
                "longitude": (Graph.nodes[u]['x'] + Graph.nodes[v]['x']) / 2,
            }

    # Salvar no arquivo JSON
    with open('crime_data.json', 'w') as f:
        json.dump(crime_data, f, indent=4)


def CrimeColorsPlot(Graph):
    max_length = max([data['danger'] for u, v, k, data in Graph.edges(keys=True, data=True)])

    fig, ax = ox.plot_graph(Graph, show=False, close=False)

    cmap = plt.cm.get_cmap('RdYlGn_r')

    for u, v, k, data in Graph.edges(keys=True, data=True):       
            length = data['danger']

            if 'geometry' in data:
                if data['danger'] > 10:
                    line = data['geometry']
                    color = cmap(length / max_length)
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