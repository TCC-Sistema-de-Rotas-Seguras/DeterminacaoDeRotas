def calcular_distancia_total(graph, route):
    distancia_total_metros = 0
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        edge_data = graph.get_edge_data(u, v)[0]
        distancia_total_metros += edge_data.get('length', 0)

    distancia_km = round(distancia_total_metros / 1000, 2)
    return f"{distancia_km:.2f} km"



def calcular_tempo_estimado(graph, route):
    tempo_total_segundos = 0
    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        edge_data = graph.get_edge_data(u, v)[0]
        length = edge_data.get('length', 0)  # em metros
        speed_kph = edge_data.get('speed_kph', 30)  # padrão se não tiver
        speed_mps = speed_kph * 1000 / 3600

        if speed_mps > 0:
            tempo_total_segundos += length / speed_mps

    horas = int(tempo_total_segundos // 3600)
    minutos = int((tempo_total_segundos % 3600) // 60)

    if horas > 0:
        return f"{horas} h {minutos} min"
    else:
        return f"{minutos} min"