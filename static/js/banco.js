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

const banco = criarBanco(); // Cria o banco
adicionarHistorico(banco, "08/04/2025", "14:20", {
    origem: criarLocalizacao("Ponto A", "Rua Teste, 123", "-23.5,-46.6"),
    destino: criarLocalizacao("Ponto B", "Av. Exemplo, 456", "-23.6,-46.7"),
    rota_safast: criarRota("2.1 km", "5 min", "<iframe>Mapa SAF</iframe>", 40, 12, 5, 7, 8),
    rota_tradicional: criarRota("2.0 km", "4 min", "<iframe>Mapa RT</iframe>", 2, 45, 3, 2, 1)
});
