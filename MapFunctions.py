from geopy.geocoders import Nominatim
import math
import osmnx as ox

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

# 
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