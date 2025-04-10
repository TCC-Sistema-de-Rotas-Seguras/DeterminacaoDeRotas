function preencherPopup(item) {
    const { data, hora, rota } = item;

    // Data e hora
    document.getElementById("span-data").innerText = `${data} ${hora}`;

    // Mapa
    document.getElementById("Container-Mapa-Resumo").innerHTML = rota.rota_safast.mapa;


    // Endereços
    document.getElementById("span-origem").innerText = rota.origem.endereco;
    document.getElementById("span-destino").innerText = rota.destino.endereco;

    // Safast
    document.getElementById("span-dist-historico").innerText = rota.rota_safast.distancia;
    document.getElementById("span-tempo-historico").innerText = rota.rota_safast.tempo;

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

    //Areas Cruzadas
    document.getElementById("span-crimes-historico").innerText = "Cruza " + rota.rota_safast.crimes.qntd_crimes + " áreas de risco";
    document.getElementById("span-crimes-rt").innerText = "Cruza " + rota.rota_tradicional.crimes.qntd_crimes + " áreas de risco";
}

function visualizarRotaHistorico(){
    banco.rota = banco.historico[banco.historico.length - 1].rota;
    loadMap(banco.rota.rota_safast.mapa, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);
    
    togglePopup("off");

    const btnOn = document.getElementById("Secondary-route-btn-on");
    const isOnVisible = btnOn.style.display !== "none";
    if (isOnVisible) {
        toggleSecondaryRoute()
    }
}