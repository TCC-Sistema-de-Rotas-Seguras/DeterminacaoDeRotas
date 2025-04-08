import os
import osmnx as ox
import networkx as nx
from tqdm import tqdm

# ____ Diretório dos Grafos ____ 
Graph_folder = "./Data/GraphParts/"
Merged_Graph_filename = "Merged_Graph.graphml"

# Listar todos os arquivos de grafos gerados
graph_files = [f for f in os.listdir(Graph_folder) if f.endswith(".graphml")]

# Carregar o primeiro grafo
merged_graph = ox.load_graphml(os.path.join(Graph_folder, graph_files[0]))

# Iterar sobre os arquivos de grafos restantes e juntar com o grafo já carregado
for graph_file in tqdm(graph_files[1:], desc="Mesclando Grafos"):
    if graph_file != "Merged_Graph.graphml":
        # Carregar o grafo do arquivo
        current_graph = ox.load_graphml(os.path.join(Graph_folder, graph_file))
        
        # Juntar os grafos (se houver sobreposição de nós, elas serão unidas)
        merged_graph = nx.compose(merged_graph, current_graph)

# Salvar o grafo combinado em um novo arquivo .graphml
ox.save_graphml(merged_graph, os.path.join(Graph_folder, Merged_Graph_filename))

# Opcional: visualizar o grafo combinado
# ox.plot_graph(merged_graph)
