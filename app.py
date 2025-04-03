# ____ Bibliotecas Externas ____
from flask import Flask, jsonify, request, render_template
import osmnx as ox
import os
import time

# ____ Bibliotecas Internas ____
from Core.MapFunctions import centro_e_raio, RoutePlot, FoliumMap
from Core.AStar import RotaAStar
from Core.AStar_NMF import RotaAStar_NMF
from Core.Djikstra import RotaDijkstra

# ___ Bibliotecas AWS ____
import io
import boto3
import tempfile
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# # ____ Configuração do download AWS ____
# s3 = boto3.client('s3')

# # Arquivo e Bucket da AWS
# bucket_name = 'tcc-grafocriminal'  
# file_name = 'Merged_Graph.graphml'  

# # Carrega o arquivo do S3 para um objeto em memória e loada o grafo
# try:
#     file_obj = io.BytesIO()
#     s3.download_fileobj(bucket_name, file_name, file_obj)
#     file_obj.seek(0)
    
#     # Carrega o grafo a partir do objeto em memória
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.graphml') as temp_file:
#         temp_file.write(file_obj.read())
#         temp_file.close()
#         Graph = ox.load_graphml(temp_file.name)

#     print("Grafo carregado com sucesso!")

# except NoCredentialsError:
#     print("Erro: Credenciais AWS não encontradas.")
# except Exception as e:
#     print(f'Ocorreu um erro ao carregar o arquivo: {e}')
#     raise

Graph = ox.load_graphml("Data/Graphs/Merged_Graph_Aplicado.graphml")

# Erro gerado ainda nao compreendido, mas nao funciona sem isso
for u, v, data in Graph.edges(data=True):
    if "weight" in data:
        data["weight"] = float(data["weight"])

@app.route('/', methods=['GET'])
def principal():
    api_key = os.getenv('GOOGLE_API_KEY')
    
    return render_template('Principal.html', api_key=api_key)

@app.route('/return_map', methods=['GET'])
def return_map():
    print("Iniciando a execução do endpoint /return_map")
    start_fulltime = time.time()

    origin = request.args.get("origin")
    destination = request.args.get("destination")
    # parameter = request.args.get("route_parameter")
    # algorithm = request.args.get("algorithm")

    if not origin or not destination:
        return jsonify(error="Erro: Parâmetros 'origin' e 'destination' são obrigatórios."), 400
    

    try:
        Origin_point = tuple(map(float, origin.split(',')))
        Destination_point = tuple(map(float, destination.split(',')))
    except (ValueError, TypeError):
        return jsonify(error="Erro: Formato inválido. Use LAT,LON para origem e destino."), 400

        
    # if algorithm == "Dijkstra":
    #     Route = RotaDijkstra(Graph, Origin_point, Destination_point)
    # elif algorithm == "AStar":
    #     Route = RotaAStar(Graph, Origin_point, Destination_point, parameter)
    # else:
    #     return jsonify(error="Erro: Algoritmo inválido. Use 'Dijkstra' ou 'AStar'."), 400


    Rota_Dijkstra = RotaDijkstra(Graph, Origin_point, Destination_point, "length")

    Rota_AStar = RotaAStar(Graph, Origin_point, Destination_point, "weight")
    Rota_AStar_length = RotaDijkstra(Graph, Origin_point, Destination_point, "length")

    Rota_AStar_manha = RotaAStar_NMF(Graph, Origin_point, Destination_point,0, "weight_manha")
    # Rota_AStar_tarde = RotaAStar_NMF(Graph, Origin_point, Destination_point,1, "weight_tarde")
    # Rota_AStar_noite = RotaAStar(Graph, Origin_point, Destination_point,2, "weight_noite")

    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)

    start_time = time.time()
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Rota_AStar, Rota_AStar_length, Rota_AStar_manha)
    end_time = time.time()
    print("Tempo de execução FoliumMap:", end_time - start_time)

    end_fulltime = time.time()
    print("Tempo de execução Total:", end_fulltime - start_fulltime)

    return jsonify(mapa_html=mapa_html)

