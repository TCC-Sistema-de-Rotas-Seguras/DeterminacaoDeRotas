from Core.Nmf import main_nmf
import osmnx as ox
import os


# Função para calcular o peso personalizado considerando distância e perigo
def custom_weight(graph):
    alpha = 1  # Fator para a distância
    beta = 10   # Fator para o perigo (ajuste conforme necessário)

    for u, v, data in graph.edges(data=True):
        # Obtém a distância da aresta
        distance = data.get("length")

        data["danger"] = int(data.get("danger", 0))
        danger = data.get("danger", 0)  # Assume perigo 0 caso não esteja definido

        data['weight'] = alpha * distance + beta * danger

    return graph

# Função para calcular o peso personalizado considerando distância, perigo e componentes NMF por período
def custom_weight_NMF(graph):
    alpha = 1  # Fator para a distância
    beta = 10   # Fator para o perigo (ajuste conforme necessário)

    # Ajuste do índice de período
    periodo_index = {"manha": 0, "tarde": 1, "noite": 2}

    for i in range(3):
        index_periodo = {v: k for k, v in periodo_index.items()} # Cria um dicionário reverso
        nome_periodo = index_periodo.get(i) # Obtém o nome do período correspondente ao índice

        weight_key = f"weight_{nome_periodo}"  # Define a chave dinamicamente
        print(f"Calculando pesos: {weight_key}")
        
        for u, v, data in graph.edges(data=True):
            # Obtém a distância da aresta
            distance = data.get("length")

            # Ajusta os valores de perigo com base nos componentes NMF para o período específico
            penalty = float(data.get(f"nmf_component_{i + 1}", 0))  # Garantir que seja numérico
            
            # Calcula o peso da aresta, combinando distância e perigo
            data[weight_key] = alpha * distance + beta * penalty

    return graph

# ____ Diretório dos Grafos ____ 
Graph_folder = "./Data/Graphs/"
Merged_Graph_filename = "Merged_Graph"

print("Carregando o grafo...")
Graph = ox.load_graphml(os.path.join(Graph_folder, Merged_Graph_filename + ".graphml"))

print("Aplicando NMF e atribuindo os componentes ao grafo...")
Graph = main_nmf(Graph) 

print("Aplicando o Weight padrão (Atributo 'weight')...")
Graph = custom_weight(Graph)

print("Aplicando o Weight para os períodos do dia...")
Graph = custom_weight_NMF(Graph)

print("Salvando o grafo...")
ox.save_graphml(Graph, os.path.join(Graph_folder, Merged_Graph_filename + "_NMF.graphml"))
