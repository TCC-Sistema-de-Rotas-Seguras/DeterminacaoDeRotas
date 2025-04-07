# ____ Bibliotecas Externas ____
from flask import Flask, jsonify, request, render_template
import osmnx as ox
import os
import time

# ____ Bibliotecas Internas ____
from Core.MapFunctions import centro_e_raio, RoutePlot, FoliumMap, gerarMapaPadrao
from Core.AStar import RotaAStar
from Core.AStar_NMF import RotaAStar_NMF
from Core.Djikstra import RotaDijkstra
from Core.Route import calcular_distancia_total, calcular_tempo_estimado

# ___ Bibliotecas AWS ____
import io
import boto3
import tempfile
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# ____ Configuração do download AWS ____
s3 = boto3.client('s3')

# Arquivo e Bucket da AWS
bucket_name = 'tcc-grafocriminal'  
file_name = 'Merged_Graph_NMF.graphml'  

if not os.path.exists("./Data/Graphs/" + file_name):
    # Carrega o arquivo do S3 para um objeto em memória e loada o grafo
    try:
        file_obj = io.BytesIO()
        s3.download_fileobj(bucket_name, file_name, file_obj)
        file_obj.seek(0)
        
        # Carrega o grafo a partir do objeto em memória
        with tempfile.NamedTemporaryFile(delete=False, suffix='.graphml') as temp_file:
            temp_file.write(file_obj.read())
            temp_file.close()
            Graph = ox.load_graphml(temp_file.name)

        print("Grafo carregado com sucesso!")
    except NoCredentialsError:
        print("Erro: Credenciais AWS não encontradas.")
    except Exception as e:
        print(f'Ocorreu um erro ao carregar o arquivo: {e}')
        raise
else:
    # Se o arquivo já existe, carrega o grafo diretamente do disco
    Graph = ox.load_graphml("./Data/Graphs/" + file_name)
    

# Erro gerado ainda nao compreendido, mas nao funciona sem isso
for u, v, data in Graph.edges(data=True):
    if "weight" in data:
        data["weight"] = float(data["weight"])
for u, v, data in Graph.edges(data=True):
    if "weight_manha" in data:
        data["weight_manha"] = float(data["weight_manha"])
for u, v, data in Graph.edges(data=True):
    if "weight_manha" in data:
        data["weight_tarde"] = float(data["weight_manha"])
for u, v, data in Graph.edges(data=True):
    if "weight_manha" in data:
        data["weight_noite"] = float(data["weight_manha"])

@app.route('/', methods=['GET'])
def principal():
    api_key = os.getenv('GOOGLE_API_KEY')
    return render_template('Principal.html', api_key=api_key)

@app.route('/mapa', methods=['GET'])
def mapa():
    return gerarMapaPadrao((-23.724025035844765, -46.579387193595984))

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


    # Rota_Crime = RotaAStar(Graph, Origin_point, Destination_point, "weight")
    Rota_Crime = RotaAStar_NMF(Graph, Origin_point, Destination_point, 0, "weight_manha")
    
    Rota_Crime_Tempo = calcular_tempo_estimado(Graph, Rota_Crime)
    print("Rota_Crime_Tempo:", Rota_Crime_Tempo)

    Rota_Crime_Distancia = calcular_distancia_total(Graph, Rota_Crime)
    print("Rota_Crime_Distancia:", Rota_Crime_Distancia)

    Rota_length = RotaDijkstra(Graph, Origin_point, Destination_point, "length")

    Rota_length_tempo = calcular_tempo_estimado(Graph, Rota_length)
    print("Rota_length_tempo:", Rota_length_tempo)

    Rota_length_distancia = calcular_distancia_total(Graph, Rota_length)
    print("Rota_length_distancia:", Rota_length_distancia)

    # Rota_AStar_manha = RotaAStar_NMF(Graph, Origin_point, Destination_point, 0, "weight_manha")

    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)

    start_time = time.time()

    mapa_html_principal = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Rota_Crime)
    mapa_html_secundario = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Rota_Crime, Rota_length)

    end_time = time.time()
    print("Tempo de execução FoliumMap:", end_time - start_time)

    end_fulltime = time.time()
    print("Tempo de execução Total:", end_fulltime - start_fulltime)

    return jsonify(

        mapa_html_principal=mapa_html_principal,
        distancia_principal=Rota_Crime_Distancia,
        tempo_estimado_principal=Rota_Crime_Tempo,

        mapa_html_secundario=mapa_html_secundario,
        distancia_secundario=Rota_length_distancia,
        tempo_estimado_secundario=Rota_length_tempo,
                
    )

