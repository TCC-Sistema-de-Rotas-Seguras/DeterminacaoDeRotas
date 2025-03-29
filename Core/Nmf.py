import osmnx as ox
import numpy as np
from sklearn.decomposition import NMF

# Função para extrair a matriz de crimes do grafo
def extract_crime_matrix(Graph):
    # Armazenar as informações de crimes por aresta
    edge_ids = []
    crime_data = []

    for u, v, k, data in Graph.edges(keys=True, data=True):
        # Pegando os dados de crime por período
        crimes_manha = int(data.get("manha", 0))
        crimes_tarde = int(data.get("tarde", 0))
        crimes_noite = int(data.get("noite", 0))
        
        # Verificando se o valor de "danger" é maior que 1
        danger = int(data.get("danger", 0))  # Pegando o valor de 'danger'
        if danger <= 2:  # Ajustando o critério de 'danger' para permitir mais arestas
            continue  # Se danger <= 2, ignorar essa aresta (não adiciona ao NMF)

        # Associando a aresta com seus dados de crime
        edge_ids.append((u, v, k))  # Identificador da aresta
        crime_data.append([crimes_manha, crimes_tarde, crimes_noite])  # Dados de crime

    # Transformar os dados de crime em uma matriz
    crime_matrix = np.array(crime_data)
    return edge_ids, crime_matrix


# Função para deslocar os valores para não-negativos
def shift_to_positive(matrix):
    # Subtrai o valor mínimo de cada coluna para garantir que todos os valores sejam não-negativos
    min_values = np.min(matrix, axis=0)
    matrix_shifted = matrix - min_values
    return matrix_shifted

# Função para aplicar NMF
def apply_nmf(crime_matrix, n_components=3):
    # Garantir que todos os valores na matriz de crimes são não-negativos
    crime_matrix_shifted = shift_to_positive(crime_matrix)

    if np.all(crime_matrix_shifted == 0):
        raise ValueError("Crime matrix is all zeros after shifting.")

    # Aplicando o NMF com 10.000 iterações (sem limite real de iterações)
    nmf_model = NMF(n_components=n_components, init='random', random_state=42, max_iter=10000000, l1_ratio=0.5, alpha_W=0.1, alpha_H=0.1)
    W = nmf_model.fit_transform(crime_matrix_shifted)
    H = nmf_model.components_

    return W, H


# Função para associar os componentes NMF com as arestas usando o atributo "d8"
def assign_nmf_features_to_graph(Graph, edge_ids, W, print_process=True):
    # Para cada aresta e seus respectivos componentes NMF
    for i, (u, v, k) in enumerate(edge_ids):
        weights = W[i]  # Componentes NMF correspondentes à aresta
        
        # Atribuindo os componentes NMF para esta aresta, baseado no índice de cada componente
        for j, w in enumerate(weights):
            attr_name = f"nmf_component_{j+1}"
            Graph.edges[u, v, k][attr_name] = float(w)  # Adiciona o atributo à aresta específica
            if print_process:  # Condicional para controlar o print
                print(f"Processando aresta ID {k} ({u}, {v}) com valor {attr_name}: {w}")
    return Graph


# Função para salvar os dados de NMF em um arquivo de texto
def write_nmf_output_to_file(edge_ids, W, H, output_filename="aresta_nmf_output.txt"):
    with open(output_filename, "w") as file:
        # Escrever informações sobre as arestas e seus componentes NMF
        for edge_id, weights in zip(edge_ids, W):
            file.write(f"Aresta ID: {edge_id}\n")
            file.write(f"Componentes NMF: {', '.join([str(w) for w in weights])}\n")
            file.write("\n")  # Linha em branco entre as entradas

        # Escrever a matriz W
        file.write("\nMatriz W (arestas x componentes):\n")
        for row in W:
            file.write(", ".join([str(w) for w in row]) + "\n")
        
        # Escrever a matriz H
        file.write("\nMatriz H (componentes x períodos de tempo):\n")
        for row in H:
            file.write(", ".join([str(h) for h in row]) + "\n")


# Função principal
def main_nmf(graphml_path, n_components=3):
    Graph = ox.load_graphml(graphml_path)
    edge_ids, crime_matrix = extract_crime_matrix(Graph)

    W, H = apply_nmf(crime_matrix, n_components=n_components)
    Graph = assign_nmf_features_to_graph(Graph, edge_ids, W, print_process=False)  # Desativar o print após NMF

    # Salvar as arestas e componentes NMF em um arquivo de texto
    write_nmf_output_to_file(edge_ids, W, H)

    # Imprimir a matriz de crimes para depuração
    print("Matriz de crimes antes de NMF:")
    print(crime_matrix)
    
    # Exibir a matriz W e H para verificar a decomposição
    print("Matriz W (arestas x componentes):")
    print(W)
    print("Matriz H (componentes x períodos de tempo):")
    print(H)

    ox.save_graphml(Graph, "Data/Graphs/Graph_with_NMF.graphml")
    return Graph, edge_ids, crime_matrix, W, H


# Caminho do grafo e execução do NMF
graph_path = "./Data/Graphs/Graph.graphml"
graph, edge_ids, crime_matrix, W, H = main_nmf(graph_path)
