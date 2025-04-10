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
            
            # Adiciona a linha ao mapa
            folium.PolyLine(line_coords, color=cor, weight=5, opacity=0.7).add_to(mapa)

def PlotPontosCrimes(mapa, rota, grafo):
    lista_crimes = {
        "baixo_risco" : [],
        "medio_risco" : [],
        "alto_risco" : []
    }

    cores = ["orange", "red", "black"]
    parametro = "danger"
    
    # Itera sobre os pontos da rota e adiciona marcadores de perigo
    for i in range(len(rota) - 1):

        # Pega os nós u e v da rota
        u, v = rota[i], rota[i + 1]

        #  Pega os dados da aresta entre os nós u e v
        edge_data = grafo.get_edge_data(u, v)

        # Itera sobre os dados da aresta
        for data in edge_data.values():
            QntdCrimes = int(data.get(parametro, 0))
            
            # Adicionar ponto de perigo (marcador preto)
            if QntdCrimes >= 5:
                if "geometry" in data:
                    # Pega o primeiro ponto da linha
                    lon, lat = list(data["geometry"].coords)[0]
                else:
                    # Usa o ponto inicial da aresta (nó u)
                    lat = grafo.nodes[u]["y"]
                    lon = grafo.nodes[u]["x"]

                if 5 <= QntdCrimes <= 12:
                    cor = cores[0]
                    lista_crimes["baixo_risco"].append(
                        {
                            "lat": lat,
                            "lon": lon,
                        }
                    )
                elif 13 <= QntdCrimes <= 20:
                    cor = cores[1]
                    lista_crimes["medio_risco"].append(
                        {
                            "lat": lat,
                            "lon": lon,
                        }
                    )
                elif QntdCrimes > 20:
                    cor = cores[2]
                    lista_crimes["alto_risco"].append(
                        {
                            "lat": lat,
                            "lon": lon,
                        }
                    )

                folium.Marker(
                    location=(lat, lon),
                    popup=f"Crimes: {data.get(parametro)}",
                    icon=folium.Icon(color=cor, icon="info-sign")
                ).add_to(mapa)

    return lista_crimes;

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
    
    
    # Adicionar a rota ao mapa
    PlotRota(RouteCrime, Graph, mapa_principal, "blue")
    PlotRota(RouteCrime, Graph, mapa_secundario, "blue")
    PlotRota(RouteLenght, Graph, mapa_secundario, "red")

    # Adicionar pontos de perigo ao mapa
    PlotPontosCrimes(mapa_principal, RouteCrime, Graph)
    lista_crimes_1 = PlotPontosCrimes(mapa_secundario, RouteCrime, Graph)
    lista_crimes_2 = PlotPontosCrimes(mapa_secundario, RouteLenght, Graph)


    return mapa_principal._repr_html_(), mapa_secundario._repr_html_(), lista_crimes_1, lista_crimes_2

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
