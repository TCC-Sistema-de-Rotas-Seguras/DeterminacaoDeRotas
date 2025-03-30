from flask import Flask, jsonify, request, render_template
import osmnx as ox
from Core.MapFunctions import centro_e_raio, RoutePlot, FoliumMap
from Core.AStar import RotaAStar
import os
import time

app = Flask(__name__)

# Carregar o grafo uma vez ao iniciar a API
Graph_folder = "./Data/Graphs/"
Graph_filename = "Graph.graphml"
Graph = ox.load_graphml(Graph_folder + Graph_filename)

@app.route('/', methods=['GET'])
def show_map():
    # Carregar a chave da API do Google Maps do arquivo .env
    api_key = os.getenv('GOOGLE_API_KEY')
    
    # Passar a chave da API para o template
    return render_template('Principal.html', api_key=api_key)

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

    print(mapa_html)
    return jsonify(mapa_html=mapa_html)