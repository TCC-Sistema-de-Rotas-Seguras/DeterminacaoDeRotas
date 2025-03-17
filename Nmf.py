# Nmf.py

import osmnx as ox
import numpy as np
from sklearn.decomposition import NMF
from sklearn.preprocessing import MinMaxScaler

# Função para extrair a matriz de crimes do grafo
def extract_crime_matrix(Graph):
    ruas = []  # Lista para armazenar os nomes das ruas
    crime_data = []  # Lista para armazenar os dados de crimes
    seen_streets = set()  # Conjunto para garantir que as ruas sejam únicas

    # Iterar sobre as arestas do grafo para extrair as informações de crimes por período
    for u, v, k, data in Graph.edges(keys=True, data=True):
        street_name = data.get("street_name", f"Rua {u}-{v}")  # Obtendo o nome da rua
        
        # Garantir que os valores de crimes sejam inteiros
        crimes_manha = int(data.get("manha", 0))  # Quantidade de crimes pela manhã
        crimes_tarde = int(data.get("tarde", 0))  # Quantidade de crimes à tarde
        crimes_noite = int(data.get("noite", 0))  # Quantidade de crimes à noite
        
        danger = data.get("danger", 0)  # Verificando o valor de "danger"

        # Verificar se o valor de "danger" é 1, se sim, desconsiderar essa aresta
        if danger == 1:
            continue  # Pular para a próxima aresta

        # Ignorar ruas duplicadas e com contagem de crimes zero
        if isinstance(street_name, str) and street_name not in seen_streets and (crimes_manha > 0 or crimes_tarde > 0 or crimes_noite > 0):
            seen_streets.add(street_name)  # Adicionando a rua ao conjunto para garantir unicidade
            ruas.append(street_name)
            crime_data.append([crimes_manha, crimes_tarde, crimes_noite])
    
    # Convertendo para matriz NumPy (apenas os dados de crimes)
    crime_matrix = np.array(crime_data)

    return ruas, crime_matrix

# Função para aplicar NMF
def apply_nmf(crime_matrix, n_components=2):
    # Normalizando a matriz de crimes com MinMaxScaler para garantir que os valores sejam não-negativos
    scaler = MinMaxScaler()  # Usando MinMaxScaler em vez de StandardScaler
    crime_matrix_scaled = scaler.fit_transform(crime_matrix)

    # Aplicando NMF
    nmf_model = NMF(n_components=n_components, init='random', random_state=42, max_iter=500, l1_ratio=0.5, alpha_W=0.1, alpha_H=0.1)
    
    # Ajustando o modelo NMF
    W = nmf_model.fit_transform(crime_matrix_scaled)
    H = nmf_model.components_

    return W, H

# Função principal que usa as funções acima
def main_nmf(graphml_path):
    # Carregando o grafo do arquivo .graphml
    Graph = ox.load_graphml(graphml_path)

    # Extraindo a matriz de crimes
    ruas, crime_matrix = extract_crime_matrix(Graph)

    # Aplicando NMF
    W, H = apply_nmf(crime_matrix)

    return ruas, crime_matrix, W, H
