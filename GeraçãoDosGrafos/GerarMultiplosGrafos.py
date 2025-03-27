import os
import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np
from Core.Crimes import CrimeLocations, FilterCrimes, CrimeAplication, GraphConversionToHotSpots


# ____ Variáveis Configuráveis ____
BOs_folder = "./Data/Bos/"
Graph_folder = "./Data/GraphParts/"

# _____ Criar Pastas _____
os.makedirs(Graph_folder, exist_ok=True)
os.makedirs(BOs_folder, exist_ok=True)

# ____ Geração de Mapa de Regiões ____
# Definição da área de cobertura (São Paulo e São Bernardo do Campo)
lat_min, lat_max = -23.75, -23.40  # Limites aproximados de latitude
lon_min, lon_max = -46.75, -46.40  # Limites aproximados de longitude

Graph_radio = 1000  # Raio de 1 km
hex_spacing = (Graph_radio * 1.2) / 111320  # Ajuste fino para cobrir toda a área

# Gerar coordenadas em grade hexagonal ajustada para eliminar espaços vazios
Graph_Locations = []
lat = lat_min
row_offset = 0
while lat <= lat_max:
    lon = lon_min + (row_offset * hex_spacing / 2)
    while lon <= lon_max:
        Graph_Locations.append((lat, lon))
        lon += hex_spacing * np.sqrt(3) * 0.85  # Ajustar espaçamento lateral para minimizar sobreposição
    lat += hex_spacing * 0.75  # Ajustar espaçamento vertical para minimizar sobreposição
    row_offset = 1 - row_offset  # Alterna deslocamento para formar a grade hexagonal

print("Quantidade de Grafos:",len(Graph_Locations))

# Localização de Crimes
Locations = CrimeLocations(BOs_folder)

# ____ Geração Incremental de Grafos ____
for i, location in enumerate(Graph_Locations):
    Graph_filename = f"Graph_{i}.graphml"
    Graph_path = os.path.join(Graph_folder, Graph_filename)

    if os.path.exists(Graph_path):
        print(f"Grafo {i} já gerado. Pulando...")
        continue  # Pula se o grafo já existe

    print(f"Gerando grafo {i}...")

    # Filtrando Crimes
    FilteredLocations = FilterCrimes(location, Graph_radio, Locations)

    try:
        Graph = ox.graph.graph_from_point(location, dist=Graph_radio, network_type="drive")
    except ValueError as e:
        print(f"Erro ao gerar grafo na localização {location}: {e}")
        continue  # Pula para o próximo ponto

    # Aplicando peso dos crimes no grafo 
    Graph = CrimeAplication(Graph, FilteredLocations)

    # Salvar Grafo
    ox.save_graphml(Graph, Graph_path)

    print(f"Grafo {i} salvo em {Graph_path}")

print("Processo concluído. Todos os grafos disponíveis foram gerados.")
