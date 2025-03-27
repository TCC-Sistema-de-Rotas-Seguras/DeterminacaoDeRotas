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
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAjTTCjSinrsbN-vTLKd4_ha20D1IVo1lo&libraries=places&callback=initAutocomplete" async defer></script>
            <script>
                let autocompleteOrigin, autocompleteDestination;

                function initAutocomplete() {
                    // Configura o autocompletar para o campo de origem
                    autocompleteOrigin = new google.maps.places.Autocomplete(
                        document.getElementById("origin"),
                        {
                            bounds: new google.maps.LatLngBounds(
                                new google.maps.LatLng(-23.9, -46.8), // Sudoeste de SP
                                new google.maps.LatLng(-23.3, -46.3)  // Nordeste de SP
                            ),
                            strictBounds: true
                        }
                    );
                    
                    // Configura o autocompletar para o campo de destino
                    autocompleteDestination = new google.maps.places.Autocomplete(
                        document.getElementById("destination"),
                        {
                            bounds: new google.maps.LatLngBounds(
                                new google.maps.LatLng(-23.9, -46.8), // Sudoeste de SP
                                new google.maps.LatLng(-23.3, -46.3)  // Nordeste de SP
                            ),
                            strictBounds: true
                        }
                    );

                    autocompleteOrigin.addListener('place_changed', function() {
                        var place = autocompleteOrigin.getPlace();
                        console.log(place);
                        if (!place.geometry) {
                            console.log("Endereço não encontrado.");
                            return;
                        }
                        document.getElementById('origin_coords').value = place.geometry.location.lat() + ',' + place.geometry.location.lng();
                    });

                    autocompleteDestination.addListener('place_changed', function() {
                        var place = autocompleteDestination.getPlace();
                        console.log(place);
                        if (!place.geometry) {
                            console.log("Endereço não encontrado.");
                            return;
                        }
                        document.getElementById('destination_coords').value = place.geometry.location.lat() + ',' + place.geometry.location.lng();
                    });
                }

                function loadMap() {
                    var origin_coords = document.getElementById('origin_coords').value;
                    var destination_coords = document.getElementById('destination_coords').value;

                    if (!origin_coords || !destination_coords) {
                        alert("Por favor, selecione ambos os endereços.");
                        return;
                    }

                    fetch(`/return_map?origin=${origin_coords}&destination=${destination_coords}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById("map-container").innerHTML = data.mapa_html;
                        })
                        .catch(error => console.error("Erro ao carregar o mapa:", error));
                }
            </script>
            <style>
                /* Seu CSS aqui */
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
                    height: 33vh;
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

                /* Estiliza o fundo da lista de sugestões */
                .pac-container {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
                    font-family: Arial, sans-serif;
                    width: 400px !important; /* Aumenta a largura */
                    max-width: 90%;
                    font-size: 18px;
                }

                /* Itens individuais da lista */
                .pac-item {
                    padding: 15px; /* Aumenta o espaçamento */
                    font-size: 14px;
                    color: #333;
                    display: flex;
                    align-items: center; /* Alinha o ícone com o texto */
                }

                /* Mudar a cor do item quando passa o mouse */
                .pac-item:hover {
                    background-color: #f1f1f1;
                }

                /* Destacar a parte do endereço sugerido */
                .pac-item .pac-item-query {
                    font-weight: bold;
                    color: #000;
                }

                /* Remove o ícone padrão do Google */
                .pac-icon {
                    display: none;
                }

                /* Adiciona um novo ícone ao lado do endereço */
                .pac-item::before {
                    content: "📍"; /* Ícone de localização personalizado */
                    font-size: 20px;
                    margin-right: 10px;
                    display: inline-block;
                }

                /* Remove o "Powered by Google" */
                .pac-container:after {
                    display: none !important;
                }
                                  
                .pac-item-query + span::before {
                    content: "("; /* Adiciona parêntese de abertura */
                }
                                  
                                  
                .pac-item-query + span::after {
                    content: ")"; /* Adiciona parêntese de fechamento */
                }

                                  
            </style>
        </head>
        <body>
            <h1>Mapa com Rota</h1>
            <div>
                <label for="origin">Origem:</label>
                <input type="text" id="origin" name="origin" required>
                <input type="hidden" id="origin_coords">
                <br>
                <label for="destination">Destino:</label>
                <input type="text" id="destination" name="destination" required>
                <input type="hidden" id="destination_coords">
                <br>
                <button type="button" onclick="loadMap()">Carregar Mapa</button>
            </div>
            <div id="map-container"></div>
        </body>
        </html>
    """)

@app.route('/return_address', methods=['GET'])
def return_address():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    address = request.args.get("endereco")
    if not address:
        return jsonify(error="Erro: Parâmetro 'endereco' é obrigatório."), 400

    coordinates = obter_geolocalizacao_google(address, api_key)
    if not coordinates:
        return jsonify(error="Erro: Não foi possível obter as coordenadas para o endereço fornecido."), 400

    return jsonify(coordinates=coordinates)

@app.route('/return_map', methods=['GET'])
def return_map():
    start_fulltime = time.time()

    origin_str = request.args.get("origin")
    destination_str = request.args.get("destination")

    if not origin_str or not destination_str:
        return jsonify(error="Erro: Parâmetros 'origin' e 'destination' são obrigatórios."), 400

    try:
        Origin_point = tuple(map(float, origin_str.split(',')))
        Destination_point = tuple(map(float, destination_str.split(',')))
    except (ValueError, TypeError):
        return jsonify(error="Erro: Formato inválido. Use LAT,LON para origem e destino."), 400

    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)
    Route_AStar = RotaAStar(Graph, Origin_point, Destination_point, "lenght")

    start_time = time.time()
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar)
    end_time = time.time()
    print("Tempo de execução FoliumMap:", end_time - start_time)

    end_fulltime = time.time()
    print("Tempo de execução Total:", end_fulltime - start_fulltime)

    return jsonify(mapa_html=mapa_html)

if __name__ == '__main__':
    app.run(debug=True)