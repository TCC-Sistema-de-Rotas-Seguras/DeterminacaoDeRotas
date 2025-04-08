
import folium
from branca.element import Figure


# Criar um mapa sem os controles de zoom e sem atribuição de copyright
m = folium.Map(
    location=(-23.726077856276497, -46.580417161816634), 
    zoom_start=18, 
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
html = m._repr_html_()
with open("mapa.html", "w") as file:
    file.write(html)