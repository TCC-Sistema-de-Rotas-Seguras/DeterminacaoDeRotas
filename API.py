from flask import Flask, jsonify, request, render_template_string
import Crimes
import osmnx as ox
from MapFunctions import centro_e_raio, RoutePlot, FoliumMap, obter_geolocalizacao_google
from AStar import RotaAStar
import os
from dotenv import load_dotenv
import time


app = Flask(__name__)

# Carregar o grafo uma vez ao iniciar a API
Graph_folder = "./Data/Graphs/"
Graph_filename = "Graph.graphml"
Graph = ox.load_graphml(Graph_folder + Graph_filename)

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
                                                
                    // Fazer requisição para buscar a geolocalização dos endereços
                    fetch(`/return_address?endereco=${origin}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                alert(data.error);
                                return;
                            }

                            var origin_coords = data.coordinates; // Coleta as coordenadas de origem

                            fetch(`/return_address?endereco=${destination}`)
                                .then(response => response.json())
                                .then(data => {
                                    if (data.error) {
                                        alert(data.error);
                                        return;
                                    }

                                    var destination_coords = data.coordinates; // Coleta as coordenadas de destino
                                  
                                    // Fazer requisição para gerar o mapa com as coordenadas obtidas
                                    fetch(`/return_map?origin=${origin_coords}&destination=${destination_coords}`)
                                        .then(response => response.json())
                                        .then(data => {
                                            document.getElementById("map-container").innerHTML = data.mapa_html;
                                        })
                                        .catch(error => console.error("Erro ao carregar o mapa:", error));
                                })
                                .catch(error => console.error("Erro ao buscar destino:", error));
                        })
                        .catch(error => console.error("Erro ao buscar origem:", error));
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
                <label for="origin">Origem (Endereço):</label>
                <input type="text" id="origin" name="origin" required>
                <br>
                <label for="destination">Destino (Endereço):</label>
                <input type="text" id="destination" name="destination" required>
                <br>
                <button type="button" onclick="loadMap()">Carregar Mapa</button>
            </div>
            <div id="map-container" class="map-container"></div>
        </body>
        </html>
    """)

@app.route('/return_address', methods=['GET'])
def return_address():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    address = request.args.get("endereco")
    print(address)
    if not address:
        return jsonify(error="Erro: Parâmetro 'endereco' é obrigatório."), 400

    # Obter geolocalização
    coordinates = obter_geolocalizacao_google(address, api_key)

    if not coordinates:
        return jsonify(error="Erro: Não foi possível obter as coordenadas para o endereço fornecido."), 400

    return jsonify(coordinates=coordinates)

@app.route('/return_map', methods=['GET'])
def return_map():
    start_fulltime = time.time()

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

    # ____ Determinação de Rota ____ 
    Route_AStar = RotaAStar(Graph, Origin_point, Destination_point, "lenght")

    # _____ Determinar Hotspots _____
    # start_time = time.time()
    # Hotspots = Crimes.GraphConversionToHotSpots(Graph)
    # end_time = time.time()
    # print("Tempo de Carregar gerar os hotspots: ", end_time - start_time)

    start_time = time.time()
    # Gerar mapa HTML
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar)
    end_time = time.time()
    print("Tempo de execução FoliumMap: ", end_time - start_time)

    end_fulltime = time.time()
    print("Tempo de execução Total: ", end_fulltime - start_fulltime)

    return jsonify(mapa_html=mapa_html)

if __name__ == '__main__':
    app.run(debug=True)
