window.addEventListener("DOMContentLoaded", () => {
    const historicoLista = document.getElementById("historico-lista");

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
        banco.historico.forEach((item,index) => {
            const score = parseFloat(getIndiceSeguranca(item.rota)).toFixed(1);
            const cor = getColor(score);

            const card = document.createElement("div");
            card.className = "card-historico";

            const info = document.createElement("div");
            info.className = "info-rota";

            info.innerHTML = `
                <div><strong>${item.rota.origem.endereco}</strong></div>
                <div>${item.rota.destino.endereco}</div>
                <div style="font-size: 12px; color: gray;">${item.data} ${item.hora}</div>
            `;

            const indicador = document.createElement("div");
            indicador.className = "indice-seguranca";
            indicador.style.backgroundColor = cor;
            indicador.textContent = score;

            card.appendChild(info);
            card.appendChild(indicador);
            historicoLista.appendChild(card);
            card.addEventListener("click", () => {
                window.location.href = `/static/template/Histórico.html?id=${index}`;
            });    
        });

            
    }

    carregarHistorico();
});
