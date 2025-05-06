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

def PlotRota(rota, grafo, mapa, cor="blue"):
    route_points = []  # Para calcular o bounding box

    # Itera sobre as arestas da rota e adiciona linhas ao mapa
    for i in range(len(rota) - 1):
        # Pega os nós u e v da rota
        u, v = rota[i], rota[i + 1]

        # Pega os dados da aresta entre os nós u e v
        edge_data = grafo.get_edge_data(u, v)

        # Itera sobre os dados da aresta
        for data in edge_data.values():

            # verifica se a aresta tem geometria
            if "geometry" in data:
                # Pega os pontos da linha
                line_coords = [(lat, lon) for lon, lat in data["geometry"].coords]
            else:
                # Se não houver geometria, usa os nós u e v
                line_coords = [(grafo.nodes[u]["y"], grafo.nodes[u]["x"]),
                               (grafo.nodes[v]["y"], grafo.nodes[v]["x"])]
            
            route_points.extend(line_coords)
            # Adiciona a linha ao mapa
            folium.PolyLine(line_coords, color=cor, weight=5, opacity=0.7).add_to(mapa)
    
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
    mapa.location = map_center
    mapa.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

from geopy.distance import geodesic
from collections import deque

def PlotPontosCrimes(mapa, rota, grafo, nivel_vizinhos=5):
    lista_crimes = {
        "baixo_risco": [],
        "medio_risco": [],
        "alto_risco": []
    }

    cores = ["orange", "red", "black"]
    parametro = "danger"

    def ja_adicionado(lat, lon, lista):
        return any(p["lat"] == lat and p["lon"] == lon for p in lista)

    # Parte 1: Adiciona crimes diretamente nas arestas da rota
    for i in range(len(rota) - 1):
        u, v = rota[i], rota[i + 1]
        edge_data = grafo.get_edge_data(u, v)

        for data in edge_data.values():
            QntdCrimes = int(data.get(parametro, 0))

            if QntdCrimes >= 5:
                if "geometry" in data:
                    lon, lat = list(data["geometry"].coords)[0]
                else:
                    lat = grafo.nodes[u]["y"]
                    lon = grafo.nodes[u]["x"]

                if 5 <= QntdCrimes <= 12:
                    cor = cores[0]
                    if not ja_adicionado(lat, lon, lista_crimes["baixo_risco"]):
                        lista_crimes["baixo_risco"].append({"lat": lat, "lon": lon})
                elif 13 <= QntdCrimes <= 20:
                    cor = cores[1]
                    if not ja_adicionado(lat, lon, lista_crimes["medio_risco"]):
                        lista_crimes["medio_risco"].append({"lat": lat, "lon": lon})
                elif QntdCrimes > 20:
                    cor = cores[2]
                    if not ja_adicionado(lat, lon, lista_crimes["alto_risco"]):
                        lista_crimes["alto_risco"].append({"lat": lat, "lon": lon})

                folium.Marker(
                    location=(lat, lon),
                    popup=f"Crimes: {data.get(parametro)}",
                    icon=folium.Icon(color=cor, icon="info-sign")
                ).add_to(mapa)

    # Parte 2: Adiciona crimes em vizinhos até o nível desejado
    visitados = set(rota)
    fila = deque([(n, 0) for n in rota])  # (nó, nível)

    while fila:
        atual, nivel = fila.popleft()

        if nivel >= nivel_vizinhos:
            continue

        for vizinho in grafo.neighbors(atual):
            if vizinho in visitados:
                continue
            visitados.add(vizinho)

            lat_viz = grafo.nodes[vizinho]["y"]
            lon_viz = grafo.nodes[vizinho]["x"]

            # distancia = geodesic((lat_viz, lon_viz), (lat_atual, lon_atual)).meters
            # if distancia <= raio_metros:
            edge_data = grafo.get_edge_data(atual, vizinho)
            for data in edge_data.values():
                QntdCrimes = int(data.get(parametro, 0))
                if QntdCrimes >= 5:
                    if 5 <= QntdCrimes <= 12:
                        cor = cores[0]
                    elif 13 <= QntdCrimes <= 20:
                        cor = cores[1]
                    elif QntdCrimes > 20:
                        cor = cores[2]

                    folium.Marker(
                        location=(lat_viz, lon_viz),
                        popup=f"Crimes ao redor (nível {nivel+1}): {QntdCrimes}",
                        icon=folium.Icon(color=cor, icon="warning")
                    ).add_to(mapa)

            # Enfileira o próximo nível
            fila.append((vizinho, nivel + 1))

    return lista_crimes



def CriarMapa(Graph_Location, Origin_point, Destination_point):

    # Criar um mapa sem os controles de zoom e sem atribuição de copyright
    mapa = folium.Map(
        location=Graph_Location, 
        zoom_start=15, 
        zoom_control=False, 
        control_scale=False,
        tiles=None  # Remove o mapa padrão que contém a atribuição de copyright
    )

    # Remover o logo @foliummap
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr=" ",  # Define um espaço em branco para evitar o erro
        name="Mapa Limpo"
    ).add_to(mapa)

    # Adicionar ponto de origem
    folium.Marker(
        location=Origin_point,
        popup="Origem",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(mapa)
    
    # Adicionar ponto de destino
    folium.Marker(
        location=Destination_point,
        popup="Destino",
        icon=folium.Icon(color="blue", icon="flag")
    ).add_to(mapa)

    # Remover o logo @foliummap
    mapa.get_root().header.render()
    figure = Figure()
    figure.add_child(mapa)
    figure.html.add_child(folium.Element("<style>.leaflet-control-attribution { display: none !important; }</style>"))

    return mapa


def FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, RouteCrime, RouteLenght):
    """
    Gera um mapa interativo usando Folium com a rota corretamente alinhada às ruas.
    
    Retorna:
    - O HTML do mapa gerado
    """

    # Criar um mapa sem os controles de zoom e sem atribuição de copyright
    mapa_principal = CriarMapa(Graph_Location, Origin_point, Destination_point)
    mapa_secundario = CriarMapa(Graph_Location, Origin_point, Destination_point)
    mapa_principal_semcrimes = CriarMapa(Graph_Location, Origin_point, Destination_point)
    mapa_secundario_semcrimes = CriarMapa(Graph_Location, Origin_point, Destination_point)

    
    
    # Adicionar a rota ao mapa
    PlotRota(RouteCrime, Graph, mapa_principal, "blue")
    PlotRota(RouteCrime, Graph, mapa_secundario, "blue")
    PlotRota(RouteLenght, Graph, mapa_secundario, "red")

    PlotRota(RouteCrime, Graph, mapa_principal_semcrimes, "blue")
    PlotRota(RouteCrime, Graph, mapa_secundario_semcrimes, "blue")
    PlotRota(RouteLenght, Graph, mapa_secundario_semcrimes, "red")


    # Adicionar pontos de perigo ao mapa
    PlotPontosCrimes(mapa_principal, RouteCrime, Graph)
    lista_crimes_1 = PlotPontosCrimes(mapa_secundario, RouteCrime, Graph)
    lista_crimes_2 = PlotPontosCrimes(mapa_secundario, RouteLenght, Graph)

    

    return mapa_principal._repr_html_(), mapa_principal_semcrimes._repr_html_(), mapa_secundario._repr_html_(), mapa_secundario_semcrimes._repr_html_(), lista_crimes_1, lista_crimes_2

def gerarMapaPadrao(location):
    # Criar um mapa sem os controles de zoom e sem atribuição de copyright
    m = folium.Map(
        location=location, 
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

    # Remover o logo @foliummap
    m.get_root().header.render()
    figure = Figure()
    figure.add_child(m)
    figure.html.add_child(folium.Element("<style>.leaflet-control-attribution { display: none !important; }</style>"))

    # Escreve o html em um arquivo txt
    return m._repr_html_()

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
