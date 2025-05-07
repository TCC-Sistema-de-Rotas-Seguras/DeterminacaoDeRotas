import osmnx as ox
import networkx as nx
from shapely.geometry import LineString
from tqdm import tqdm  # Adiciona barra de progresso

# Caminho correto do grafo
file_path = r"F:\Github\DeterminacaoDeRotas\Estudo\SBCCrimesAumentados\Merged_Graph_NMF.graphml"

# 1. Carrega o grafo do arquivo
G = ox.load_graphml(file_path)

# 2. Pega o polígono de São Bernardo do Campo
gdf_sbc = ox.geocode_to_gdf("São Bernardo do Campo, São Paulo, Brazil")
polygon_sbc = gdf_sbc.geometry.iloc[0]

# 3. Itera nas arestas com barra de progresso
edges = list(G.edges(keys=True, data=True))
for u, v, k, data in tqdm(edges, desc="Atualizando atributos NMF"):
    # Verifica geometria
    geom = data.get('geometry')
    if geom is None:
        point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
        point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
        geom = LineString([point_u, point_v])

    # Se intersecta com SBC, multiplica os componentes NMF
    if geom.intersects(polygon_sbc):
        for attr in ['nmf_component_1', 'nmf_component_2', 'nmf_component_3']:
            if attr in data:
                try:
                    data[attr] = str(float(data[attr]) * 2)
                except ValueError:
                    print(f"Erro ao converter o atributo {attr} na aresta ({u}, {v}, {k})")

# 4. Salva o grafo com os valores alterados
ox.save_graphml(G, filepath=r"F:\Github\DeterminacaoDeRotas\Estudo\SBCCrimesAumentados\Merged_Graph_NMF_SBCAumentado.graphml")
