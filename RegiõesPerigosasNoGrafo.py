import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import math

# _____Função Haversine para calcular a distância_____
def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância entre dois pontos (latitude e longitude) em metros.
    """
    R = 6371000  # Raio da Terra em metros
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_point_within_radius(center, radius, point):
    """
    Verifica se um ponto está dentro de um raio específico ao redor do centro.
    """
    lat1, lon1 = center
    lat2, lon2 = point
    distance = haversine(lat1, lon1, lat2, lon2)
    return distance <= radius

# _____Extraindo Regiões Perigosas_____
arquivo_csv = "Data/teste.csv"

df = pd.read_csv(arquivo_csv)

# Remover duplicados e valores inválidos
df = df.drop_duplicates(subset=["latitude", "longitude"])
latitude = df["latitude"].dropna().astype(float)
longitude = df["longitude"].dropna().astype(float)

latitude = latitude[latitude != 0.0].tolist()
longitude = longitude[longitude != 0.0].tolist()

print(f"Quantidade total de pontos perigosos: {len(latitude)}")

if len(latitude) != len(longitude):
    print("Erro: Quantidade de Valores Diferentes")
    exit()

# _____Configurações iniciais_____
Fei_Location = (-23.72403491298448, -46.579397903870166)  # Localização inicial
map_radio = 2000  # Raio do mapa em metros

# Gerar o grafo a partir da localização central
Graph = ox.graph.graph_from_point(Fei_Location, dist=map_radio, network_type="drive")

# _____Filtrar pontos perigosos dentro do raio_____
dangerous_points = []
for lat, lon in zip(latitude, longitude):
    if is_point_within_radius(Fei_Location, map_radio, (lat, lon)):
        dangerous_points.append((lat, lon))

print(f"Pontos perigosos dentro do raio: {len(dangerous_points)}")

# _____Plotar o grafo e os pontos perigosos_____
fig, ax = ox.plot_graph(Graph, show=False, close=False)

# Adicionar os pontos perigosos ao gráfico
for lat, lon in dangerous_points:
    ax.scatter(lon, lat, c='red', s=50, label="Ponto Perigoso", alpha=0.7)

# Remover duplicatas na legenda
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')

plt.show()
