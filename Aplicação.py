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
def custom_weight_NMF(graph, periodo):
    alpha = 1  # Fator para a distância
    beta = 10   # Fator para o perigo (ajuste conforme necessário)

    # Ajuste do índice de período
    periodo_index = {"manha": 0, "tarde": 1, "noite": 2}
    periodo_idx = periodo_index.get(periodo, 0)  # Default é manhã
    weight_key = f"weight_{periodo}"  # Define a chave dinamicamente
    
    for u, v, data in graph.edges(data=True):
        # Obtém a distância da aresta
        distance = data.get("length")

        # Ajusta os valores de perigo com base nos componentes NMF para o período específico
        crime = float(data.get(f"nmf_component_{periodo_idx + 1}", 0))  # Garantir que seja numérico
        
        # Calcula o perigo total como o componente NMF específico para o período
        penalty = crime
        
        # Calcula o peso da aresta, combinando distância e perigo
        data[weight_key] = alpha * distance + beta * penalty

    return graph

# ____ Diretório dos Grafos ____ 
Graph_folder = "./Data/Graphs/"
Merged_Graph_filename = "Parcial_Merged_Graph"

print("Carregando o grafo...")
Graph = ox.load_graphml(os.path.join(Graph_folder, Merged_Graph_filename + ".graphml"))

print("Aplicando NMF e atribuindo os componentes ao grafo...")
Graph = main_nmf(Graph) 

print("Aplicando o Weight padrão (Atributo 'weight')...")
Graph = custom_weight(Graph)

print("Aplicando o Weight para o período da manhã (Atributo 'weight_manha')...")
Graph = custom_weight_NMF(Graph, 0)

print("Aplicando o Weight para o período da tarde (Atributo 'weight_tarde')...")
Graph = custom_weight_NMF(Graph, 1)

print("Aplicando o Weight para o período da noite (Atributo 'weight_noite')...")
Graph = custom_weight_NMF(Graph, 2)

ox.save_graphml(Graph, os.path.join(Graph_folder, Merged_Graph_filename + "_Aplicado.graphml"))
