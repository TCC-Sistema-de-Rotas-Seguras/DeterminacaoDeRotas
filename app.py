from flask import Flask, jsonify, request, render_template
import osmnx as ox
from Core.MapFunctions import centro_e_raio, RoutePlot, FoliumMap
from Core.AStar import RotaAStar
from Core.Djikstra import RotaDijkstra
import os
import time
import io
import boto3
import tempfile
from botocore.exceptions import NoCredentialsError

# Verificar se o diretório existe
if os.path.exists('Templates'):
    # Listar todos os arquivos e subdiretórios dentro do diretório templates
    for root, dirs, files in os.walk('Templates'):
        for file in files:
            print(os.path.join(root, file))
else:
    print(f'O diretório "{'Templates'}" não existe.')


app = Flask(__name__)

# Configuração do cliente S3
s3 = boto3.client('s3')

# Nome do bucket e do arquivo que você quer ler
bucket_name = 'tcc-grafocriminal'  # Substitua pelo seu bucket
file_name = 'Merged_Graph.graphml'  # Substitua pelo nome do seu arquivo

try:
    # Tente carregar o grafo a partir do S3
    file_obj = io.BytesIO()
    s3.download_fileobj(bucket_name, file_name, file_obj)
    file_obj.seek(0)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.graphml') as temp_file:
        temp_file.write(file_obj.read())  # Escrever o conteúdo do arquivo no arquivo temporário
        temp_file.close()
        Graph = ox.load_graphml(temp_file.name)

    print("Grafo carregado com sucesso!")

except NoCredentialsError:
    print("Erro: Credenciais AWS não encontradas.")
except Exception as e:
    print(f'Ocorreu um erro ao carregar o arquivo: {e}')
    raise


@app.route('/', methods=['GET'])
def principal():
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
    Route_Djiktra = RotaDijkstra(Graph, Origin_point, Destination_point)
    # Route_AStar = RotaAStar(Graph, Origin_point, Destination_point, "weight")

    start_time = time.time()
    mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_Djiktra)
    # mapa_html = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Route_AStar)
    end_time = time.time()
    print("Tempo de execução FoliumMap:", end_time - start_time)

    end_fulltime = time.time()
    print("Tempo de execução Total:", end_fulltime - start_fulltime)

    return jsonify(mapa_html=mapa_html)

