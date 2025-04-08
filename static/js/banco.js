function criarBanco() {
    return {
        rota: {
            origem: criarLocalizacao("", "", ""),
            destino: criarLocalizacao("", "", ""),
            rota_safast: criarRota(null, null, "", null, null, null, null, null),
            rota_tradicional: criarRota(null, null, "", null, null, null, null, null)
        },
        historico: []
    };
}

function criarLocalizacao(nome, endereco, geo_localizacao) {
    return {
        nome,
        endereco,
        geo_localizacao
    };
    
}

function criarRota(distancia, tempo, mapa, qntd_evitados, qntd_crimes, qntd_risco, qntd_medio_risco, qntd_alto_risco) {
    return {
        distancia,
        tempo,
        mapa,
        crimes: {
            qntd_evitados,
            qntd_crimes,
            qntd_risco,
            qntd_medio_risco,
            qntd_alto_risco
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