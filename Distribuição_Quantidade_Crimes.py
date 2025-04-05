import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import Counter
import random

# ===== CONFIGURAÇÕES =====
bin_size = 1
danger_min = 5    # ⬅️ Novo: limite mínimo
danger_limit = 99  # ⬅️ Limite máximo

# ===== CRIAÇÃO DO GRAFO =====
print("🔧 Carregando grafo...")
G = ox.load_graphml("./Data/Graphs/Merged_Graph_NMF.graphml")

print(f"✅ Total de arestas no grafo: {G.number_of_edges()}\n")

# ===== COLETA DE DADOS =====
print(f"📊 Coletando valores de 'danger' (entre {danger_min} e {danger_limit})...")
danger_values = []
ignored_above = 0
ignored_below = 0

for _, _, data in tqdm(G.edges(data=True), desc="🔍 Lendo arestas"):
    danger = int(data.get("danger", 0))
    if danger_min <= danger <= danger_limit:
        danger_values.append(danger)
    elif danger < danger_min:
        ignored_below += 1
    elif danger > danger_limit:
        ignored_above += 1

print(f"✅ Coleta concluída!")
print(f"  ➤ Arestas consideradas: {len(danger_values)}")
print(f"  ❌ Ignoradas abaixo de {danger_min}: {ignored_below}")
print(f"  ❌ Ignoradas acima de {danger_limit}: {ignored_above}\n")

# ===== AGRUPAMENTO EM BINS =====
print("📦 Agrupando valores em faixas...")
bins = list(range(danger_min, danger_limit + bin_size, bin_size))

def get_bin_label(danger):
    bin_start = (danger // bin_size) * bin_size
    bin_end = bin_start + bin_size - 1
    return f"{bin_start}-{bin_end}"

danger_bins = [get_bin_label(d) for d in danger_values]
danger_counter = Counter(danger_bins)

# Ordenando os rótulos
ordered_labels = sorted(danger_counter.keys(), key=lambda x: int(x.split("-")[0]))
frequencies = [danger_counter[label] for label in ordered_labels]

print("📋 Frequência por faixa:")
for label in ordered_labels:
    print(f"  ➤ {label}: {danger_counter[label]}")

# ===== PLOT =====
print("\n📈 Plotando gráfico de barras agrupado...")
plt.figure(figsize=(12, 6))
plt.bar(ordered_labels, frequencies, color='seagreen')
plt.xlabel("Faixa de perigo (danger)")
plt.ylabel("Quantidade de Arestas")
plt.title(f"Distribuição de Periculosidade (de {danger_min} até {danger_limit})")
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
