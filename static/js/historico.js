document.addEventListener("DOMContentLoaded", () => {
    const botaoHistorico = document.getElementById("btn-historico");

    if (botaoHistorico) {
        botaoHistorico.addEventListener("click", () => {
            if (banco.historico.length > 0) {
                const ultimo = banco.historico[banco.historico.length - 1];
                preencherPopup(ultimo);
            }
        });
    }
});

function preencherPopup(item) {
    const { data, hora, rota } = item;

    // Data e hora
    document.getElementById("span-data").innerText = `${data} ${hora}`;

    // Endereços
    document.getElementById("span-origem").innerText = rota.origem.endereco;
    document.getElementById("span-destino").innerText = rota.destino.endereco;

    // Safast
    document.getElementById("span-dist").innerText = rota.rota_safast.distancia;
    document.getElementById("span-tempo").innerText = rota.rota_safast.tempo;

    // Tradicional
    document.getElementById("span-dist-rt").innerText = rota.rota_tradicional.distancia;
    document.getElementById("span-tempo-rt").innerText = rota.rota_tradicional.tempo;

    // Áreas evitadas
    const btnEvitadas = document.getElementById("span-crimes-evitados");
    btnEvitadas.innerText = `${rota.rota_safast.crimes.qntd_evitados} ÁREAS DE RISCO EVITADAS`;

    // Bolinhas de risco
    document.getElementById("span-alto-risco").innerText = rota.rota_safast.crimes.qntd_alto_risco;
    document.getElementById("span-medio-risco").innerText = rota.rota_safast.crimes.qntd_medio_risco;
    document.getElementById("span-baixo-risco").innerText = rota.rota_safast.crimes.qntd_risco;

    //Areas evitadas
    document.getElementById("span-crimes").innerText = "Cruza " + rota.rota_safast.crimes.qntd_crimes + " áreas de risco";
    document.getElementById("span-crimes-rt").innerText = "Cruza " + rota.rota_tradicional.crimes.qntd_crimes + " áreas de risco";
}

window.addEventListener("DOMContentLoaded", () => {
    const historicoLista = document.getElementById("historico-lista");

    function getIndiceSeguranca(rota) {
        const crimes = rota.rota_safast.crimes;
        const total = crimes.qntd_risco + crimes.qntd_medio_risco + crimes.qntd_alto_risco;
        const maxScore = 10;

        if (total <= 3) return 8 + Math.random();      // Muito seguro
        if (total <= 10) return 5 + Math.random() * 2;  // Médio
        return 3 + Math.random() * 2;                   // Inseguro
    }

    function getColor(score) {
        if (score >= 7) return "#4CAF50";   // Verde
        if (score >= 5) return "#2196F3";   // Azul
        return "#757575";                   // Cinza escuro
    }

    function carregarHistorico() {
        banco.historico.forEach(item => {
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
        });
    }

    carregarHistorico();
});
