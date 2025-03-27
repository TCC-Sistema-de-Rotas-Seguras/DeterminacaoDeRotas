import folium
import osmnx as ox
import networkx as nx

# ____ Diretório do Grafo Unificado ____
Merged_Graph_filename = "./Data/GraphParts/Merged_Graph.graphml"

# Carregar o grafo unificado
G = ox.load_graphml(Merged_Graph_filename)

# Obter as coordenadas (latitude, longitude) dos nós do grafo
nodes, _ = ox.graph_to_gdfs(G)

# Obter o centro do grafo (média das coordenadas)
center_lat = nodes['y'].mean()
center_lon = nodes['x'].mean()

# Criar o mapa com Folium centrado na região do grafo
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Adicionar marcadores para os nós
for _, row in nodes.iterrows():
    folium.CircleMarker(
        location=[row['y'], row['x']],
        radius=2,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(m)

# Adicionar as arestas como linhas conectando os nós
for u, v, data in G.edges(data=True):
    u_lat, u_lon = nodes.loc[u]['y'], nodes.loc[u]['x']
    v_lat, v_lon = nodes.loc[v]['y'], nodes.loc[v]['x']
    folium.PolyLine(
        locations=[(u_lat, u_lon), (v_lat, v_lon)],
        color='gray',
        weight=1.5,
        opacity=0.5
    ).add_to(m)

# Exibir o mapa
m.save("graph_map.html")
