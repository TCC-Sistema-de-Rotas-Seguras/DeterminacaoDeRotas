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
            loadMap();
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
            loadMap();
        }
    });
}

function loadMap() {
    var origin_coords = document.getElementById('origin_coords').value;
    var destination_coords = document.getElementById('destination_coords').value;

    if (!origin_coords || !destination_coords) {
        alert("Por favor, selecione ambos os endereços.");
        return;
    }

    fetch(`/return_map?origin=${origin_coords}&destination=${destination_coords}`)
        .then(response => response.json())
        .then(data => {
            console.log("Mapa carregado com sucesso:", data.mapa_html);
            document.getElementById("map-container").innerHTML = data.mapa_html;

            // Aguarde um curto tempo para garantir que o HTML seja inserido
            setTimeout(() => {
                let mapDiv = document.querySelector("#map-container > div > div");
                if (mapDiv) {
                    mapDiv.style.position = ""; // Ou simplesmente remova a propriedade
                    mapDiv.style.paddingBottom = ""; // Se quiser remover a altura baseada em padding
                }
            }, 100);

        })
        .catch(error => console.error("Erro ao carregar o mapa:", error));
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