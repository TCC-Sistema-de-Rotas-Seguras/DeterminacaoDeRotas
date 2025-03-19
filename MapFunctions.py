from geopy.geocoders import Nominatim
import math
import osmnx as ox
import folium

# _____Função Haversine_____
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

# _____Função para obter a geolocalização de um endereço_____
def get_geolocation(address):
    # Inicializar o geolocalizador
    geolocator = Nominatim(user_agent="geoapi")

    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None

def RoutePlot(ax, Graph, Route_AStar):
    # Adiciona a rota ao gráfico já existente
    ox.plot_graph_route(
        Graph,
        Route_AStar,
        route_color="blue",
        route_linewidth=3,
        ax=ax,  # Usa o eixo existente
        show=False,
        close=False
    )

def centro_e_raio(p1, p2):
    # Centro do círculo (média das coordenadas)
    centro = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    
    # Raio do círculo (metade da distância entre os pontos)
    raio = haversine(*p1, *p2) / 2
    
    return centro, raio

def FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route, Hotspots):
    """
    Gera um mapa interativo usando Folium com a rota corretamente alinhada às ruas.

    Retorna:
    - O HTML do mapa gerado
    """
    
    # Criar um mapa com Folium
    m = folium.Map(location=Graph_Location, zoom_start=15)

    # Adicionar ponto de origem (marcador verde)
    folium.Marker(
        location=Origin_point,
        popup="Origem",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    # Adicionar ponto de destino (marcador azul)
    folium.Marker(
        location=Destination_point,
        popup="Destino",
        icon=folium.Icon(color="blue", icon="flag")
    ).add_to(m)

    # Desenhar todas as ruas do grafo para dar contexto ao mapa
    # for u, v, data in Graph.edges(data=True):
    #     if "geometry" in data:
    #         line_coords = [(lat, lon) for lon, lat in data["geometry"].coords]
    #     else:
    #         line_coords = [(Graph.nodes[u]["y"], Graph.nodes[u]["x"]), (Graph.nodes[v]["y"], Graph.nodes[v]["x"])]

    #     folium.PolyLine(line_coords, color="gray", weight=1, opacity=0.5).add_to(m)

    # Adicionar a rota calculada (seguindo as ruas corretamente)
    route_lines = []
    for i in range(len(Route) - 1):
        u, v = Route[i], Route[i + 1]
        edge_data = Graph.get_edge_data(u, v)

        for data in edge_data.values():
            if "geometry" in data:
                route_lines.extend([(lat, lon) for lon, lat in data["geometry"].coords])
            else:
                route_lines.append((Graph.nodes[u]["y"], Graph.nodes[u]["x"]))
                route_lines.append((Graph.nodes[v]["y"], Graph.nodes[v]["x"]))

    folium.PolyLine(route_lines, color="blue", weight=5, opacity=0.7, popup="Rota").add_to(m)

    # Adiciona os hotspots ao mapa
    # for lat, lon in Hotspots:
    #     folium.CircleMarker(
    #         location=[lat, lon],
    #         radius=20,
    #         color="red",
    #         fill=True,
    #         fill_color="red",
    #         fill_opacity=0.6,
    #         popup=f"Hotspot: ({lat}, {lon})",
    #     ).add_to(m)

    # Salva o mapa em um arquivo HTML
    m.save("Mapa.html")

    return m._repr_html_()  # Retorna o HTML do mapa

