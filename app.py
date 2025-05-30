# ____ Bibliotecas Externas ____
from flask import Flask, jsonify, request, render_template
import osmnx as ox
import os
import time

# ____ Bibliotecas Internas ____
from Core.MapFunctions import centro_e_raio, RoutePlot, FoliumMap, gerarMapaPadrao
from Core.AStar import RotaAStar
from Core.AStar_NMF import RotaAStar_NMF
from Core.AStar_NMF_Hibrido import RotaAStar_NMF_Hibrida
from Core.Djikstra import RotaDijkstra
from Core.Route import calcular_distancia_total, calcular_tempo_estimado
from Core.Crimes import DiferencaListaCrimes, IndiceSeguranca

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
    return jsonify(mapa=gerarMapaPadrao((-23.724025035844765, -46.579387193595984)))

@app.route('/return_map', methods=['GET'])
def return_map():
    print("Iniciando a execução do endpoint /return_map")
    tempos = {}
    start_full = time.time()

    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:
        return jsonify(error="Erro: Parâmetros 'origin' e 'destination' são obrigatórios."), 400

    t0 = time.time()
    try:
        Origin_point = tuple(map(float, origin.split(',')))
        Destination_point = tuple(map(float, destination.split(',')))
    except (ValueError, TypeError):
        return jsonify(error="Erro: Formato inválido. Use LAT,LON para origem e destino."), 400
    tempos["Parsing dos parâmetros"] = time.time() - t0

    t0 = time.time()
    Rota_Crime = RotaAStar(Graph, Origin_point, Destination_point, "weight_manha")
    tempos["RotaAStar_NMF (Rota_Crime)"] = time.time() - t0

    t0 = time.time()
    Rota_Crime_Tempo = calcular_tempo_estimado(Graph, Rota_Crime)
    tempos["Tempo estimado (Rota_Crime)"] = time.time() - t0

    t0 = time.time()
    Rota_Crime_Distancia = calcular_distancia_total(Graph, Rota_Crime)
    tempos["Distância total (Rota_Crime)"] = time.time() - t0

    t0 = time.time()
    Rota_length = RotaDijkstra(Graph, Origin_point, Destination_point, "length")
    tempos["RotaDijkstra (Rota_length)"] = time.time() - t0

    t0 = time.time()
    Rota_length_tempo = calcular_tempo_estimado(Graph, Rota_length)
    tempos["Tempo estimado (Rota_length)"] = time.time() - t0

    t0 = time.time()
    Rota_length_distancia = calcular_distancia_total(Graph, Rota_length)
    tempos["Distância total (Rota_length)"] = time.time() - t0

    t0 = time.time()
    Graph_Location, Graph_radio = centro_e_raio(Origin_point, Destination_point)
    tempos["Centro e raio do mapa"] = time.time() - t0

    t0 = time.time()
    mapa_html_principal, mapa_html_principal_semcrimes, mapa_html_secundario, mapa_html_secundario_semcrimes,mapa_html_principal_comsecundarios,mapa_html_secundario_comsecundarios, lista_crimes_Rota_Crime, lista_crimes_Rota_Lenght  = FoliumMap(Graph, Graph_Location, Origin_point, Destination_point, Rota_Crime, Rota_length)
    lista_crimes_Diferenca = DiferencaListaCrimes(lista_crimes_Rota_Crime, lista_crimes_Rota_Lenght)
    tempos["FoliumMap (mapas)"] = time.time() - t0

    t0 = time.time()
    ids_crime, ids_length = IndiceSeguranca(lista_crimes_Rota_Lenght, lista_crimes_Rota_Crime)
    tempos["Indice de segurança"] = time.time() - t0

    tempos["Tempo total"] = time.time() - start_full

    print("\n--- TEMPOS DE EXECUÇÃO ---")
    for etapa, duracao in tempos.items():
        print(f"{etapa:<35}: {duracao:.4f} segundos")
    print("--------------------------\n")


    qntd_evitados_principal = len(lista_crimes_Diferenca["baixo_risco"]) + len(lista_crimes_Diferenca["medio_risco"]) +len(lista_crimes_Diferenca["alto_risco"])
    qntd_crimes_principal = len(lista_crimes_Rota_Crime["baixo_risco"]) + len(lista_crimes_Rota_Crime["medio_risco"]) + len(lista_crimes_Rota_Crime["alto_risco"])
    qtnd_evitados_baixo_risco_principal = len(lista_crimes_Diferenca["baixo_risco"])
    qtnd_evitados_medio_risco_principal = len(lista_crimes_Diferenca["medio_risco"])
    qtnd_evitados_alto_risco_principal = len(lista_crimes_Diferenca["alto_risco"])

    qntd_crimes_secundario = len(lista_crimes_Rota_Lenght["baixo_risco"]) + len(lista_crimes_Rota_Lenght["medio_risco"]) + len(lista_crimes_Rota_Lenght["alto_risco"])

    return jsonify(
        # Mapa Principal
        mapa_html_principal=mapa_html_principal,
        mapa_html_principal_semcrimes=mapa_html_principal_semcrimes,
        mapa_html_principal_comsecundarios=mapa_html_principal_comsecundarios,
        distancia_principal=Rota_Crime_Distancia,
        tempo_estimado_principal=Rota_Crime_Tempo,
        qntd_evitados_principal=qntd_evitados_principal,
        qntd_crimes_principal=qntd_crimes_principal,

        qtnd_evitados_baixo_risco_principal=qtnd_evitados_baixo_risco_principal,
        qtnd_evitados_medio_risco_principal=qtnd_evitados_medio_risco_principal,
        qtnd_evitados_alto_risco_principal=qtnd_evitados_alto_risco_principal,
        indice_seguranca_principal=ids_crime,

        # Mapa Secundário
        mapa_html_secundario=mapa_html_secundario,
        mapa_html_secundario_semcrimes=mapa_html_secundario_semcrimes,
        mapa_html_secundario_comsecundarios=mapa_html_secundario_comsecundarios,
        distancia_secundario=Rota_length_distancia,
        tempo_estimado_secundario=Rota_length_tempo,
        qntd_crimes_secundario=qntd_crimes_secundario,
        indice_seguranca_secundario=ids_length,
    )

@app.route('/return_historico')
def return_historico():
    with open('./templates/Histórico.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

@app.route('/return_interHistorico')
def return_interHistorico():
    with open('./templates/InterHistorico.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

@app.route('/return_favoritos')
def return_favoritos():
    with open('./templates/Favoritos.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content