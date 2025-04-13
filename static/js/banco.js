function criarBanco() {
    return {
        rota: {
            origem: criarLocalizacao("", "", ""),
            destino: criarLocalizacao("", "", ""),
            rota_safast: criarRota(null, null, "", "", null, null, null, null, null),
            rota_tradicional: criarRota(null, null, "", "", null, null, null, null, null)
        },
        historico: [],
        tipo_mapa_atual: {
            rota: "simples",
            crime: "ligado",
        },
        historico_carregado: null,
    };
}

function criarLocalizacao(nome, endereco, geo_localizacao) {
    return {
        nome,
        endereco,
        geo_localizacao
    };
    
}

function criarRota(distancia, tempo, mapa, mapa_semcrimes, qntd_crimes, qntd_evitados, qtnd_evitados_baixo_risco, qtnd_evitados_medio_risco, qtnd_evitados_alto_risco) {
    return {
        distancia,
        tempo,
        mapa,
        mapa_semcrimes,
        crimes: {
            qntd_crimes,
            qntd_evitados,
            qtnd_evitados_baixo_risco,
            qtnd_evitados_medio_risco,
            qtnd_evitados_alto_risco
        }
    };
}

// _____ Rota _____
function atualizarRotaBanco(banco, origem, destino, rota_safast, rota_tradicional) {
    banco.rota = {
        origem,
        destino,
        rota_safast,
        rota_tradicional
    };
}

// _____ Historicos _____
function adicionarHistorico(banco, data, hora, rota) {
    const historico = {
        data,
        hora,
        rota
    };
    banco.historico.push(historico);
}

function removerHistorico(banco, indice) {
    banco.historico.splice(indice, 1);
}