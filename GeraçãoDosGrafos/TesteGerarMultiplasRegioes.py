import folium
import numpy as np

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

# Criar o mapa centralizado na média das coordenadas
media_lat = (lat_min + lat_max) / 2
media_lon = (lon_min + lon_max) / 2
mapa = folium.Map(location=[media_lat, media_lon], zoom_start=11)

# Adicionar círculos ao mapa
for lat, lon in Graph_Locations:
    folium.Circle(
        location=[lat, lon],
        radius=Graph_radio,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.3
    ).add_to(mapa)

# Salvar e exibir o mapa
mapa.save("mapa_regioes_ajustado.html")
print("Mapa salvo como mapa_regioes_ajustado.html")
