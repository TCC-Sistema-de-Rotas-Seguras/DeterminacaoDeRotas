from flask import Flask, jsonify, request, render_template_string
import Crimes
import os
import osmnx as ox
from MapFunctions import centro_e_raio, get_geolocation, RoutePlot, FoliumMap
from AStar import RotaAStar
from Djikstra import RotaDijkstra
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/map', methods=['GET', 'POST'])
def show_map():
    # Definindo valores padrão para origem e destino
    origin_str = "-23.72401011599897, -46.5796130581241"  # FEI
    destination_str = "-23.714717997133853, -46.55373510564497"  # Outro ponto em SP

    if request.method == 'POST':
        # Pega os parâmetros do formulário (origem e destino)
        origin_str = request.form.get("origin")
        destination_str = request.form.get("destination")

        # Verifica se os parâmetros foram passados corretamente
        if not origin_str or not destination_str:
            return "Erro: Parâmetros 'origin' e 'destination' são obrigatórios.", 400

        try:
            # Converte os valores de string para tupla (latitude, longitude)
            Origin_point = tuple(map(float, origin_str.split(',')))
            Destination_point = tuple(map(float, destination_str.split(',')))
        except (ValueError, TypeError):
            return "Erro: Formato inválido. Use LAT,LON para origem e destino.", 400
    else:
        # Se for um GET, usa os valores padrão
        Origin_point = tuple(map(float, origin_str.split(',')))
        Destination_point = tuple(map(float, destination_str.split(',')))

    # ____ Variáveis Configuráveis ____
    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)

    Graph_folder = "./Data/Graphs/"
    Graph_filename = "Graph.graphml"
    Graph = ox.load_graphml(Graph_folder + Graph_filename)

    # ____ Determinação de Rota ____
    Route_AStar = RotaAStar(Graph, Origin_point, Destination_point)

    # _____ Determinar Hotspots _____
    Hotspots = Crimes.GraphConversionToHotSpots(Graph)

    # Suponha que Graph, Graph_Location, Origin_point, Destination_point, Route, e Hotspots já estejam definidos
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar, Hotspots)

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa Interativo</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    height: 100vh;
                    background-color: #f4f4f4;
                }
                .map-container {
                    width: 80%;
                    height: 33vh; /* 2/3 da tela */
                }
                .form-container {
                    margin: 20px;
                    padding: 10px;
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                input[type="text"] {
                    width: 200px;
                    padding: 5px;
                    margin: 10px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>Mapa com Rota</h1>
            <div class="form-container">
                <form method="POST" action="/map">
                    <label for="origin">Origem (Latitude, Longitude):</label>
                    <input type="text" id="origin" name="origin" value="{{ origin_str }}" required>
                    <br>
                    <label for="destination">Destino (Latitude, Longitude):</label>
                    <input type="text" id="destination" name="destination" value="{{ destination_str }}" required>
                    <br>
                    <button type="submit">Carregar Mapa</button>
                </form>
            </div>
            <div class="map-container">
                {{ mapa_html|safe }}
            </div>
        </body>
        </html>
    """, mapa_html=mapa_html, origin_str=origin_str, destination_str=destination_str)

if __name__ == '__main__':
    app.run(debug=True)
