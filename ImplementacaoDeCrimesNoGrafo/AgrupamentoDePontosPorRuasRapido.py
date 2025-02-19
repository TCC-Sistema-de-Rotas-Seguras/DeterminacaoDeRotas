import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from tqdm import tqdm
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

# _____Extraindo Regiões Perigosas_____
arquivo_csv = "Data/teste.csv"
df = pd.read_csv(arquivo_csv)

# Remover valores inválidos
latitude = df["latitude"].dropna().astype(float)
longitude = df["longitude"].dropna().astype(float)

latitude = latitude[latitude != 0.0].tolist()
longitude = longitude[longitude != 0.0].tolist()

print(f"Quantidade total de pontos perigosos: {len(latitude)}")

if len(latitude) != len(longitude):
    print("Erro: Quantidade de Valores Diferentes")
    exit()

# _____Configurações iniciais_____
Fei_Location = (-23.72403491298448, -46.579397903870166)
graph_radio = 2000

# Gerar o grafo a partir da localização central
Graph = ox.graph.graph_from_point(Fei_Location, dist=graph_radio, network_type="drive")

# _____Filtrar pontos perigosos dentro do raio_____
dangerous_points = []
for lat, lon in tqdm(zip(latitude, longitude), desc="Determinando Pontos de Crime na região"):
    if haversine(Fei_Location[0], Fei_Location[1], lat, lon) <= graph_radio:
        dangerous_points.append((lat, lon))

print(f"Pontos perigosos dentro do raio: {len(dangerous_points)}")

# _____Atribuir pesos às ruas com base nos pontos perigosos_____
street_weights = {}

# Usar osmnx para encontrar o nó mais próximo para cada ponto
for lat, lon in tqdm(dangerous_points, desc="Determinando Pesos das Ruas"):
    nearest_node = ox.distance.nearest_nodes(Graph, lon, lat)
    for u, v, k, data in Graph.edges(keys=True, data=True):
        if u == nearest_node or v == nearest_node:
            edge_id = (u, v, k)
            if edge_id not in street_weights:
                street_weights[edge_id] = 0
            street_weights[edge_id] += 1
            break
        

# _____Atribuir cores e plotar o gráfico_____
fig, ax = ox.plot_graph(Graph, show=False, close=False)

# Encontrar o maior peso
max_weight = max(street_weights.values()) if street_weights else 1  # Evitar erro se street_weights for vazio

# Definir uma paleta de cores personalizada para o gráfico
cmap = plt.cm.get_cmap('RdYlGn_r')  # Vermelho para laranja/verde para azul (inverso de 'RdYlGn')

# Plotar ruas com pesos
for u, v, k, data in Graph.edges(keys=True, data=True):
    edge_id = (u, v, k)
    if edge_id in street_weights:
        weight = street_weights[edge_id]
        # Verifique se a chave 'geometry' existe antes de acessar
        if 'geometry' in data:
            line = data['geometry']
            # Normalizar o peso para usar com a paleta de cores
            color = cmap(weight / max_weight)  # Cor proporcional ao peso
            ax.plot(*line.xy, color=color, linewidth=2)

plt.show()

total = 0
# Exibir ruas e seus pesos
for edge_id, weight in street_weights.items():
    # print(f"Rua {edge_id} tem {weight} pontos perigosos.")
    total += weight

print(f"Total de pontos perigosos: {total}")
