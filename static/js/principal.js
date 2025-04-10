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
            mapa_html_principal = data.mapa_html_principal;
            distancia_principal = data.distancia_principal;
            tempo_principal = data.tempo_estimado_principal;
            qntd_evitados_principal = data.qntd_evitados_principal;
            qntd_crimes_principal = data.qntd_crimes_principal;
            qtnd_risco_principal = data.qtnd_risco_principal;
            qtnd_medio_risco_principal = data.qtnd_medio_risco_principal;
            qtnd_alto_risco_principal = data.qtnd_alto_risco_principal;

            mapa_html_secundario = data.mapa_html_secundario;
            distancia_secundario = data.distancia_secundario;
            tempo_secundario = data.tempo_estimado_secundario;
            qntd_evitados_secundario = data.qntd_evitados_secundario;
            qntd_crimes_secundario = data.qntd_crimes_secundario;
            qtnd_risco_secundario = data.qtnd_risco_secundario;
            qtnd_medio_risco_secundario = data.qtnd_medio_risco_secundario;
            qtnd_alto_risco_secundario = data.qtnd_alto_risco_secundario;

            atualizarRotaBanco(banco, 
                criarLocalizacao(document.getElementById('origin').value, document.getElementById('origin').value, document.getElementById('origin_coords').value),
                criarLocalizacao(document.getElementById('destination').value, document.getElementById('destination').value, document.getElementById('destination_coords').value),
                criarRota(distancia_principal, tempo_principal, mapa_html_principal, qntd_evitados_principal, qntd_crimes_principal, qtnd_risco_principal, qtnd_medio_risco_principal, qtnd_alto_risco_principal),
                criarRota(distancia_secundario, tempo_secundario, mapa_html_secundario, qntd_evitados_secundario, qntd_crimes_secundario, qtnd_risco_secundario, qtnd_medio_risco_secundario, qtnd_alto_risco_secundario)
            );

            adicionarHistorico(banco, new Date().toLocaleDateString(), new Date().toLocaleTimeString(), banco.rota);
            

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

        if (pagina == "historico") {
            fetch(`/return_historico`)
            .then(response => response.text())
            .then(data => {
                document.getElementById("popup-container").innerHTML = data;
                preencherPopup(banco.historico[banco.historico.length - 1]);
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
        
        loadMap(banco.rota.rota_safast.mapa, banco.rota.rota_safast.distancia, banco.rota.rota_safast.tempo);
    // ON
    } else {
        // Esconde o OFF, mostra o ON
        btnOff.style.display = "none";
        svgOff.style.display = "none";
        btnOn.style.display = "";
        svgOn.style.display = "";

        loadMap(banco.rota.rota_tradicional.mapa, banco.rota.rota_tradicional.distancia, banco.rota.rota_tradicional.tempo);
    }
  }

window.onload = function() {
    carregarMapa();
};

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
  
var banco = criarBanco();