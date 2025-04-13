let autocompleteOrigin, autocompleteDestination;

function initAutocomplete() {
    // Configura o autocompletar para o campo de origem
    autocompleteOrigin = new google.maps.places.Autocomplete(
        document.getElementById("origin"),
        {
            bounds: new google.maps.LatLngBounds(
                new google.maps.LatLng(-23.9, -46.8), // Sudoeste de SP
                new google.maps.LatLng(-23.3, -46.3)  // Nordeste de SP
            ),
            strictBounds: true
        }
    );
    
    // Configura o autocompletar para o campo de destino
    autocompleteDestination = new google.maps.places.Autocomplete(
        document.getElementById("destination"),
        {
            bounds: new google.maps.LatLngBounds(
                new google.maps.LatLng(-23.9, -46.8), // Sudoeste de SP
                new google.maps.LatLng(-23.3, -46.3)  // Nordeste de SP
            ),
            strictBounds: true
        }
    );

    autocompleteOrigin.addListener('place_changed', function() {
        var place = autocompleteOrigin.getPlace();
        console.log(place);
        if (!place.geometry) {
            console.log("Endereço não encontrado.");
            return;
        }
        document.getElementById('origin_coords').value = place.geometry.location.lat() + ',' + place.geometry.location.lng();
    
        if(document.getElementById('destination_coords').value != "") {
            requestRoute();
            togglePopup("off");
            const btnOn = document.getElementById("Secondary-route-btn-on");
            const isOnVisible = btnOn.style.display !== "none";
            if (isOnVisible) {
                toggleSecondaryRoute()
            }
        }

    });

    autocompleteDestination.addListener('place_changed', function() {
        var place = autocompleteDestination.getPlace();
        console.log(place);
        if (!place.geometry) {
            console.log("Endereço não encontrado.");
            return;
        }
        document.getElementById('destination_coords').value = place.geometry.location.lat() + ',' + place.geometry.location.lng();
    
        if(document.getElementById('origin_coords').value != "") {
            requestRoute();
            togglePopup("off");
            const btnOn = document.getElementById("Secondary-route-btn-on");
            const isOnVisible = btnOn.style.display !== "none";
            if (isOnVisible) {
                toggleSecondaryRoute()
            }
        }
    });
}

window.initAutocomplete = initAutocomplete;

function requestRoute() {
    var origin_coords = document.getElementById('origin_coords').value;
    var destination_coords = document.getElementById('destination_coords').value;

    mostrarLoader();

    fetch(`/return_map?origin=${origin_coords}&destination=${destination_coords}`)
        .then(response => response.json())
        .then(data => {
            // Principal
            mapa_html_principal = data.mapa_html_principal;
            mapa_html_principal_semcrimes = data.mapa_html_principal_semcrimes; // Implementando
            distancia_principal = data.distancia_principal;
            tempo_principal = data.tempo_estimado_principal;

            // Crimes Principal
            qntd_crimes_principal = data.qntd_crimes_principal;
            qntd_evitados_principal = data.qntd_evitados_principal;
            qtnd_evitados_baixo_risco_principal = data.qtnd_evitados_baixo_risco_principal;
            qtnd_evitados_medio_risco_principal = data.qtnd_evitados_medio_risco_principal;
            qtnd_evitados_alto_risco_principal = data.qtnd_evitados_alto_risco_principal;

            // Secundario
            mapa_html_secundario = data.mapa_html_secundario;
            mapa_html_secundario_semcrimes = data.mapa_html_secundario_semcrimes; // Implementando
            distancia_secundario = data.distancia_secundario;
            tempo_secundario = data.tempo_estimado_secundario;

            // Crimes Secundario
            qntd_crimes_secundario = data.qntd_crimes_secundario;
            
            // Atualizar Banco
            atualizarRotaBanco(banco, 
                criarLocalizacao(document.getElementById('origin').value, document.getElementById('origin').value, document.getElementById('origin_coords').value),
                criarLocalizacao(document.getElementById('destination').value, document.getElementById('destination').value, document.getElementById('destination_coords').value),
                criarRota(distancia_principal, tempo_principal, mapa_html_principal,mapa_html_principal_semcrimes, qntd_crimes_principal, qntd_evitados_principal,  qtnd_evitados_baixo_risco_principal, qtnd_evitados_medio_risco_principal, qtnd_evitados_alto_risco_principal),
                criarRota(distancia_secundario, tempo_secundario, mapa_html_secundario,mapa_html_secundario_semcrimes, qntd_crimes_secundario, null,  null, null, null)
            );
    
            // Adicionar ao historico
            adicionarHistorico(banco, new Date().toLocaleDateString(), new Date().toLocaleTimeString(), banco.rota);
    
            // Carregar Mapa
            loadMap(banco.rota.rota_safast.mapa, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);
            

        })
        .catch(error => console.error("Erro ao carregar o mapa:", error))
        .finally(() => {
            esconderLoader();
        });

        

    

}

function loadMap(mapa, distancia, tempo) {    
    document.getElementById("map-container").innerHTML = mapa;
    document.getElementById("span-distancia").innerHTML = distancia;
    document.getElementById("span-tempo").innerHTML = tempo;

    // Aguarde um curto tempo para garantir que o HTML seja inserido
    setTimeout(() => {
        let mapDiv = document.querySelector("#map-container > div > div");
        if (mapDiv) {
            mapDiv.style.position = ""; // Ou simplesmente remova a propriedade
            mapDiv.style.paddingBottom = ""; // Se quiser remover a altura baseada em padding
        }
    }, 100);

    
}

function togglePopup(pagina) {
    var popup = document.querySelector(".popup-section");

    // Desativar
    if (popup.classList.contains("active") || pagina == "off") {

        popup.classList.remove("active");

        if (window.innerWidth <= 450) {
            anticlick = document.querySelector("#map-anti-click");
            anticlick.style.zIndex = "-1";

        }

        

    // Ativar
    } else {
        popup.classList.add("active");

        if (window.innerWidth <= 450) {
            anticlick = document.querySelector("#map-anti-click");
            anticlick.style.zIndex = "0";

        }

        // if (pagina == "historico") {
        //     fetch(`/return_historico`)
        //     .then(response => response.text())
        //     .then(data => {
        //         document.getElementById("popup-container").innerHTML = data;
        //         preencherPopup(banco.historico[banco.historico.length - 1]);
        //     })
        //     .catch(error => console.error('Erro ao carregar o HTML:', error));
        // }
        if (pagina == "historico") {
            fetch(`/return_interHistorico`)
            .then(response => response.text())
            .then(data => {
                document.getElementById("popup-container").innerHTML = data;
                carregarHistorico()
            })
            .catch(error => console.error('Erro ao carregar o HTML:', error));
        }
    }
}

function toggleSecondaryRoute() {
    const btnOn = document.getElementById("Secondary-route-btn-on");
    const svgOn = document.getElementById("Secondary-route-svg-on");
    const btnOff = document.getElementById("Secondary-route-btn-off");
    const svgOff = document.getElementById("Secondary-route-svg-off");
  
    const isOnVisible = btnOn.style.display !== "none";
  
    // OFF
    if (isOnVisible) {
        // Esconde o ON, mostra o OFF
        btnOn.style.display = "none";
        svgOn.style.display = "none";
        btnOff.style.display = "";
        svgOff.style.display = "";
        
        var mapa_carregado;
        if (banco.tipo_mapa_atual.crime == "ligado") {
            mapa_carregado = banco.rota.rota_safast.mapa
        }else if (banco.tipo_mapa_atual.crime == "desligado") {
            mapa_carregado = banco.rota.rota_safast.mapa_semcrimes
        }
        
        loadMap(mapa_carregado, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);
        banco.tipo_mapa_atual.rota = "simples";
    // ON
    } else {
        // Esconde o OFF, mostra o ON
        btnOff.style.display = "none";
        svgOff.style.display = "none";
        btnOn.style.display = "";
        svgOn.style.display = "";

        var mapa_carregado;
        if (banco.tipo_mapa_atual.crime == "ligado") {
            mapa_carregado = banco.rota.rota_tradicional.mapa
        }else if (banco.tipo_mapa_atual.crime == "desligado") {
            mapa_carregado = banco.rota.rota_tradicional.mapa_semcrimes
        }

        loadMap(mapa_carregado, banco.rota.rota_tradicional.distancia, banco.rota.rota_tradicional.tempo);
        banco.tipo_mapa_atual.rota = "dupla";

    }
}

function toggleCrimeVisualization() {
    const btnOn = document.getElementById("Crime-visualization-btn-on");
    const imgOn = document.getElementById("Crime-visualization-img-on");
    const btnOff = document.getElementById("Crime-visualization-btn-off");
    const imgOff = document.getElementById("Crime-visualization-img-off");

    const isOnVisible = btnOn.style.display !== "none";

    // OFF
    if (isOnVisible) {
        // Esconde o ON, mostra o OFF
        btnOn.style.display = "none";
        imgOn.style.display = "none";
        btnOff.style.display = "";
        imgOff.style.display = "";
        
        var mapa_carregado;
        if (banco.tipo_mapa_atual.rota == "simples") {
            mapa_carregado = banco.rota.rota_safast.mapa_semcrimes
            loadMap(mapa_carregado, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);

        }else if (banco.tipo_mapa_atual.rota == "dupla") {
            mapa_carregado = banco.rota.rota_tradicional.mapa_semcrimes
            loadMap(mapa_carregado, banco.rota.rota_tradicional.distancia, banco.rota.rota_tradicional.tempo);

        }

        banco.tipo_mapa_atual.crime = "desligado";
    // ON
    } else {
        // Esconde o OFF, mostra o ON
        btnOff.style.display = "none";
        imgOff.style.display = "none";
        btnOn.style.display = "";
        imgOn.style.display = "";

        var mapa_carregado;
        if (banco.tipo_mapa_atual.rota == "simples") {
            mapa_carregado = banco.rota.rota_safast.mapa
            loadMap(mapa_carregado, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);
        }else if (banco.tipo_mapa_atual.rota == "dupla") {
            mapa_carregado = banco.rota.rota_tradicional.mapa
            loadMap(mapa_carregado, banco.rota.rota_tradicional.distancia, banco.rota.rota_tradicional.tempo);
        }

        banco.tipo_mapa_atual.crime = "ligado";
    }
}



function carregarMapa() {
    fetch(`/mapa`)
    .then(response => response.json())
    .then(data => {
        loadMap(data.mapa, "0 Km", "0 min");
    })
    .catch(error => console.error("Erro ao carregar o mapa:", error));
}

function mostrarLoader() {
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('map-blur').style.display = 'flex';
    document.getElementById('map-blur').style.background = 'rgba(0, 0, 0, 0.6)';

    
}

function esconderLoader() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('map-blur').style.display = 'none';
    document.getElementById('map-blur').style.background = 'rgba(0, 0, 0, 0.0)';

}

function voltar() {
    // Se estiver na lista de historico
    if (document.getElementById("inter-historico")) {
        togglePopup("off")
    } 
    // Se estiver em um resumo
    else if (document.getElementById("Container-Mapa-Resumo")) {
        togglePopup('historico')
        togglePopup('historico')
    } 
}

window.onload = function() {
    carregarMapa();
};

var banco = criarBanco();