import osmnx as ox
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import math
from sklearn.cluster import DBSCAN
import numpy as np
from scipy.spatial import ConvexHull

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

# _____Aplicando DBSCAN para identificar clusters_____
# Convertendo os pontos para um formato de array NumPy
coordinates = np.array(dangerous_points)

# Aplicando DBSCAN
db = DBSCAN(eps=0.000005, min_samples=10, metric='haversine')
clusters = db.fit_predict(np.radians(coordinates))  # Convertendo para radianos para o DBSCAN

# _____Plotar o grafo e as áreas dos clusters de pontos perigosos_____
fig, ax = ox.plot_graph(Graph, show=False, close=False)

# Plotar a área de cada cluster usando a convex hull
for cluster_id in np.unique(clusters):
    if cluster_id == -1:
        # Pontos ruídos (não pertencem a nenhum cluster)
        continue

    # Pegando os pontos do cluster
    cluster_points = coordinates[clusters == cluster_id]
    
    # Calculando a Convex Hull do cluster
    if len(cluster_points) > 2:  # A convex hull só é válida para 3 ou mais pontos
        hull = ConvexHull(cluster_points)

        # Plotando a área da Convex Hull
        hull_points = np.array([cluster_points[vertex] for vertex in hull.vertices])
        hull_points = np.vstack([hull_points, hull_points[0]])  # Fechando o polígono
        ax.plot(hull_points[:, 1], hull_points[:, 0], 'r-', alpha=0.7, label=f"Cluster {cluster_id}")

# Remover duplicatas na legenda
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')

plt.show()
