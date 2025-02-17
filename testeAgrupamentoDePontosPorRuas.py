import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
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

# _____Converter o grafo para DataFrames de ruas (edges)_____
gdf_nodes, gdf_edges = ox.graph_to_gdfs(Graph)

# _____Calcular quantos pontos perigosos estão próximos de cada rua (edge)_____
street_weights = {}

for lat, lon in dangerous_points:
    point = Point(lon, lat)  # Criar o ponto perigoso
    # Encontrar a rua mais próxima
    nearest_edge = None
    min_distance = float('inf')

    for idx, row in gdf_edges.iterrows():
        line = row['geometry']  # Linha (rua) no grafo
        distance = line.distance(point)  # Calcular a distância entre o ponto e a rua

        if distance < min_distance:
            min_distance = distance
            nearest_edge = row

    # Incrementar o contador de pontos perigosos para a rua (edge) mais próxima
    if nearest_edge is not None:
        edge_id = nearest_edge.name
        if edge_id not in street_weights:
            street_weights[edge_id] = 0
        street_weights[edge_id] += 1

# _____Atribuir cores e plotar o gráfico_____
fig, ax = ox.plot_graph(Graph, show=False, close=False)

# Encontrar o maior peso
max_weight = max(street_weights.values()) if street_weights else 1  # Evitar erro se street_weights for vazio

# Definir uma paleta de cores personalizada para o gráfico
cmap = plt.cm.get_cmap('RdYlGn_r')  # Vermelho para laranja/verde para azul (inverso de 'RdYlGn')

# Plotar ruas com pesos
for idx, row in gdf_edges.iterrows():
    edge_id = row.name
    if edge_id in street_weights:
        weight = street_weights[edge_id]
        # Normalizar o peso para usar com a paleta de cores
        color = cmap(weight / max_weight)  # Cor proporcional ao peso
        ax.plot(*row['geometry'].xy, color=color, linewidth=2)

# Remover duplicatas na legenda
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')

plt.show()

# Exibir ruas e seus pesos
for edge_id, weight in street_weights.items():
    print(f"Rua {edge_id} tem {weight} pontos perigosos.")
