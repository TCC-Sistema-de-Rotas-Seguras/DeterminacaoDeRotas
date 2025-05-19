function getIndiceSeguranca(rota) {
    const crimes = rota?.rota_safast?.crimes || {};

    const evitados = crimes.qntd_evitados ?? 0;
    const baixo = crimes.qntd_risco ?? 0;
    const medio = crimes.qntd_medio_risco ?? 0;
    const alto = crimes.qntd_alto_risco ?? 0;

    const distanciaRaw = rota?.rota_safast?.distancia || "0 km";
    const distancia = parseFloat(distanciaRaw.replace("km", "").trim()) || 1;  // evita divisão por zero

    const risco_total = baixo * 0.2 + medio * 0.5 + alto * 1.0;
    const densidade_risco = risco_total / distancia;

    let indice = 10 - densidade_risco + evitados * 0.1;

    indice = Math.max(0, Math.min(10, indice));  // Garante entre 0 e 10
    return parseFloat(indice.toFixed(1));
}


function getColor(score) {
    if (score >= 7) return "#4CAF50"; // Verde — seguro
    if (score >= 4) return "#FFC107"; // Amarelo — médio
    return "#F44336";                 // Vermelho — inseguro
}


function carregarHistorico() {
    var historicoLista = document.getElementById("historico-lista");
    banco.historico.slice().reverse().forEach((item, index) => {
        // O índice original será baseado na posição do item no array original
        const realIndex = banco.historico.length - 1 - index;
    
        const card = document.createElement("div");
        card.className = "card-historico";
    
        const info = document.createElement("div");
        info.className = "info-rota";
        
        console.log(item.rota);
        console.log(item.rota.rota_safast);
        console.log(item.rota.rota_safast.crimes.indice_seguranca);
        info.innerHTML = `
        
            <section class="card-historico-top">
                <div class="iniciofim">
                    <div class="iniciofim-bola"></div>
                    <div class="iniciofim-haste"></div>
                    <div class="iniciofim-base"></div>
                </div>
                <section class="Endereço-Historico">
                    <span>${item.rota.origem.endereco}</span>
                    <span>${item.rota.destino.endereco}</span>
                </section>
            </section>
            <div style="margin-bottom: 5px;>
                <h5>Indice de Segurança Safast: ${item.rota.rota_safast.crimes.indice_seguranca}</h4>
            </div>
            <div style="font-size: 12px; color: gray;">${item.data} ${item.hora}</div>
        `;
    
        card.appendChild(info);
        historicoLista.appendChild(card);
    
        card.addEventListener("click", () => {
            fetch(`/return_historico`)
            .then(response => response.text())
            .then(data => {
                document.getElementById("popup-container").innerHTML = data;
                banco.historico_carregado = realIndex;  // Usa o índice real aqui
                preencherDadosHistorico(realIndex);    // Usa o índice real aqui
            })
            .catch(error => console.error('Erro ao carregar o HTML:', error));
        });
    });
    

        
}