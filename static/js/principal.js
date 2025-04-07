let autocompleteOrigin, autocompleteDestination;

var mapa_html_principal = null;
var distancia_principal = null;
var tempo_principal = null;

var mapa_html_secundario = null;
var distancia_secundario = null;
var tempo_secundario = null;


function carregarMapa() {
    fetch(`/mapa`)
    .then(response => response.text())
    .then(data => {
        document.getElementById("map-container").innerHTML = data;
    })
    .catch(error => console.error("Erro ao carregar o mapa:", error));

}

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
            requestMap();
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
            requestMap();
        }
    });
}

function requestMap() {
    var origin_coords = document.getElementById('origin_coords').value;
    var destination_coords = document.getElementById('destination_coords').value;

    fetch(`/return_map?origin=${origin_coords}&destination=${destination_coords}`)
        .then(response => response.json())
        .then(data => {
            mapa_html_principal = data.mapa_html_principal;
            distancia_principal = data.distancia_principal;
            tempo_principal = data.tempo_estimado_principal;

            mapa_html_secundario = data.mapa_html_secundario;
            distancia_secundario = data.distancia_secundario;
            tempo_secundario = data.tempo_estimado_secundario;

            loadMap(data.mapa_html_principal, distancia_principal, tempo_principal);
        })
        .catch(error => console.error("Erro ao carregar o mapa:", error));

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

function togglePopup() {
    console.log("Toggle Popup");
    var popup = document.querySelector(".popup-section");

    if (popup.classList.contains("active")) {

        popup.classList.remove("active");

        if (window.innerWidth <= 450) {
            anticlick = document.querySelector("#map-anti-click");
            anticlick.style.zIndex = "-1";

        }

    } else {
        popup.classList.add("active");

        if (window.innerWidth <= 450) {
            anticlick = document.querySelector("#map-anti-click");
            anticlick.style.zIndex = "0";

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
        
        loadMap(mapa_html_principal, distancia_principal, tempo_principal); // Carrega o mapa principal
    // ON
    } else {
        // Esconde o OFF, mostra o ON
        btnOff.style.display = "none";
        svgOff.style.display = "none";
        btnOn.style.display = "";
        svgOn.style.display = "";

        loadMap(mapa_html_secundario, distancia_secundario, tempo_secundario); // Carrega o mapa secundário
    }
  }

