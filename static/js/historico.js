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
