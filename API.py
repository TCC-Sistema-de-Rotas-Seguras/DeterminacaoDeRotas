from flask import Flask, jsonify, request, render_template_string
import Crimes
import osmnx as ox
from MapFunctions import centro_e_raio, get_geolocation, RoutePlot, FoliumMap
from AStar import RotaAStar
from Djikstra import RotaDijkstra

app = Flask(__name__)

@app.route('/', methods=['GET'])
def show_map():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa Interativo</title>
            <script>
                function loadMap() {
                    var origin = document.getElementById("origin").value;
                    var destination = document.getElementById("destination").value;
                    
                    fetch(`/return_map?origin=${origin}&destination=${destination}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById("map-container").innerHTML = data.mapa_html;
                        })
                        .catch(error => console.error("Erro ao carregar o mapa:", error));
                }
            </script>
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
                <label for="origin">Origem (Latitude, Longitude):</label>
                <input type="text" id="origin" name="origin" value="-23.72401011599897, -46.5796130581241" required>
                <br>
                <label for="destination">Destino (Latitude, Longitude):</label>
                <input type="text" id="destination" name="destination" value="-23.714717997133853, -46.55373510564497" required>
                <br>
                <button type="button" onclick="loadMap()">Carregar Mapa</button>
            </div>
            <div id="map-container" class="map-container"></div>
        </body>
        </html>
    """)

@app.route('/return_map', methods=['GET'])
def return_map():
    # Pega os parâmetros da URL
    origin_str = request.args.get("origin")
    destination_str = request.args.get("destination")

    if not origin_str or not destination_str:
        return jsonify(error="Erro: Parâmetros 'origin' e 'destination' são obrigatórios."), 400

    try:
        Origin_point = tuple(map(float, origin_str.split(',')))
        Destination_point = tuple(map(float, destination_str.split(',')))
    except (ValueError, TypeError):
        return jsonify(error="Erro: Formato inválido. Use LAT,LON para origem e destino."), 400

    # ____ Variáveis Configuráveis ____
    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)
    Graph_folder = "./Data/Graphs/"
    Graph_filename = "Graph.graphml"
    Graph = ox.load_graphml(Graph_folder + Graph_filename)

    # ____ Determinação de Rota ____
    Route_AStar = RotaAStar(Graph, Origin_point, Destination_point)

    # _____ Determinar Hotspots _____
    Hotspots = Crimes.GraphConversionToHotSpots(Graph)

    # Gerar mapa HTML
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar, Hotspots)

    return jsonify(mapa_html=mapa_html)

if __name__ == '__main__':
    app.run(debug=True)
