import math
import osmnx as ox
import folium
from shapely.geometry import MultiPoint
from branca.element import Figure

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


def FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route, HotspotRoute = None):
    """
    Gera um mapa interativo usando Folium com a rota corretamente alinhada às ruas.
    
    Retorna:
    - O HTML do mapa gerado
    """
    
    # Criar um mapa sem os controles de zoom e sem atribuição de copyright
    m = folium.Map(
        location=Graph_Location, 
        zoom_start=15, 
        zoom_control=False, 
        control_scale=False,
        tiles=None  # Remove o mapa padrão que contém a atribuição
    )

    # Remover o logo @foliummap
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr=" ",  # Define um espaço em branco para evitar o erro
        name="Mapa Limpo"
    ).add_to(m)

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

    # Adicionar a rota calculada (seguindo as ruas corretamente)
    route_points = []  # Para calcular o bounding box
    for i in range(len(Route) - 1):
        u, v = Route[i], Route[i + 1]
        edge_data = Graph.get_edge_data(u, v)

        for data in edge_data.values():
            # Definir a cor da linha com base no perigo
            color = "red" if float(data.get("danger", 0)) > 10 else "blue"

            if "geometry" in data:
                line_coords = [(lat, lon) for lon, lat in data["geometry"].coords]
            else:
                line_coords = [(Graph.nodes[u]["y"], Graph.nodes[u]["x"]),
                               (Graph.nodes[v]["y"], Graph.nodes[v]["x"])]

            route_points.extend(line_coords)
            folium.PolyLine(line_coords, color=color, weight=5, opacity=0.7).add_to(m)

        # Calcular o bounding box para ajustar o zoom
        points = MultiPoint(route_points)
        min_lat, min_lon, max_lat, max_lon = points.bounds

        buffer = 0.002  # Ajuste esse valor conforme necessário
        min_lat -= buffer
        max_lat += buffer
        min_lon -= buffer
        max_lon += buffer

        # Centralizar o mapa e ajustar o zoom
        map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
        m.location = map_center
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    if HotspotRoute is not None:
        # Adicionar a rota calculada (seguindo as ruas corretamente)
        route_points = []  # Para calcular o bounding box
        for i in range(len(HotspotRoute) - 1):
            u, v = HotspotRoute[i], HotspotRoute[i + 1]
            edge_data = Graph.get_edge_data(u, v)

            for data in edge_data.values():
                # Definir a cor da linha com base no perigo
                color = "red" if float(data.get("danger", 0)) > 10 else "purple"

                if "geometry" in data:
                    line_coords = [(lat, lon) for lon, lat in data["geometry"].coords]
                else:
                    line_coords = [(Graph.nodes[u]["y"], Graph.nodes[u]["x"]),
                                (Graph.nodes[v]["y"], Graph.nodes[v]["x"])]

                route_points.extend(line_coords)
                folium.PolyLine(line_coords, color=color, weight=5, opacity=0.7).add_to(m)

            # Calcular o bounding box para ajustar o zoom
            points = MultiPoint(route_points)
            min_lat, min_lon, max_lat, max_lon = points.bounds

            buffer = 0.002  # Ajuste esse valor conforme necessário
            min_lat -= buffer
            max_lat += buffer
            min_lon -= buffer
            max_lon += buffer

            # Centralizar o mapa e ajustar o zoom
            map_center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
            m.location = map_center
            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    # Remover o logo @foliummap
    m.get_root().header.render()
    figure = Figure()
    figure.add_child(m)
    figure.html.add_child(folium.Element("<style>.leaflet-control-attribution { display: none !important; }</style>"))

    return m._repr_html_()  # Retorna o HTML do mapa

# _____ Descontinuado devido implementação direto em JS ______

# def obter_geolocalizacao_google(endereco, api_key):
#     """
#     Retorna a latitude e longitude para o endereço fornecido utilizando a API do Google Maps.
    
#     Parâmetros:
#     - endereco: Endereço a ser geocodificado (ex: "Rua XV de Novembro, São Paulo, Brasil")
#     - api_key: Sua chave de API do Google Maps
    
#     Retorna:
#     - Tuple (latitude, longitude) ou None se não encontrar a localização.
#     """
#     # Inicializa o cliente do Google Maps
#     gmaps = googlemaps.Client(key=api_key)
    
#     try:
#         # Realiza a geocodificação do endereço
#         geocode_result = gmaps.geocode(endereco)
        
#         if geocode_result:
#             # Extrai a latitude e longitude do primeiro resultado
#             lat = geocode_result[0]['geometry']['location']['lat']
#             lng = geocode_result[0]['geometry']['location']['lng']
#             return lat, lng
#         else:
#             return None  # Endereço não encontrado
#     except Exception as e:
#         print(f"Erro ao geocodificar o endereço: {e}")
#         return None
