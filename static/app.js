// Žemėlapis

const map = L.map("map").setView(
    [55.1694, 23.8813],
    7
);

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// Žemėlapio objektai

let locationMarker = null;
let nearestMarker = null;
let secondNearestMarker = null;
let thirdNearestMarker = null;

let nearestLine = null;
let secondNearestLine = null;
let thirdNearestLine = null;

let windStationMarkers = [];


// Dabartiniai rezultatai

let currentLocation = null;
let currentNearest = null;
let currentSecond = null;
let currentThird = null;


// Vietovių paieška

let autocompleteTimer = null;
let autocompleteController = null;
let autocompleteResults = [];


// Žymeklių kūrimas

function createMarkerIcon(symbol, className) {

    return L.divIcon({

        className: "",

        html:
            '<div class="station-marker ' +
            className +
            '">' +
            symbol +
            "</div>",

        iconSize: [30, 30],

        iconAnchor: [15, 15],

        popupAnchor: [0, -17]

    });

}


const locationIcon =
    createMarkerIcon(
        "●",
        "location-marker"
    );


const nearestIcon =
    createMarkerIcon(
        "★",
        "primary-marker"
    );


const secondNearestIcon =
    createMarkerIcon(
        "▲",
        "secondary-marker"
    );


const thirdNearestIcon =
    createMarkerIcon(
        "■",
        "tertiary-marker"
    );


// Vėjo stoties žymeklis

const windStationIcon =
    L.divIcon({

        className: "",

        html:
            '<div class="wind-station-map-marker">' +
            "•" +
            "</div>",

        iconSize: [18, 18],

        iconAnchor: [9, 9],

        popupAnchor: [0, -9]

    });


// Tikriname vėjo filtrą

function isWindOnlyEnabled() {

    return document.getElementById(
        "windOnly"
    ).checked;

}


// Apsaugome tekstą

function escapeHtml(value) {

    const element =
        document.createElement(
            "div"
        );

    element.textContent =
        value ?? "";

    return element.innerHTML;

}


// Išvalome žemėlapį

function clearMapObjects() {

    const objects = [

        locationMarker,

        nearestMarker,

        secondNearestMarker,

        thirdNearestMarker,

        nearestLine,

        secondNearestLine,

        thirdNearestLine

    ];


    objects.forEach(

        object => {

            if (object) {

                map.removeLayer(
                    object
                );

            }

        }

    );


    windStationMarkers.forEach(

        marker => {

            map.removeLayer(
                marker
            );

        }

    );


    windStationMarkers = [];


    locationMarker = null;

    nearestMarker = null;

    secondNearestMarker = null;

    thirdNearestMarker = null;

    nearestLine = null;

    secondNearestLine = null;

    thirdNearestLine = null;

}


// Atnaujiname stočių informaciją

function updateResults(
    first,
    second,
    third,
    message
) {

    document.getElementById(
        "primaryName"
    ).textContent =

        first
            ? first.name
            : "Nėra";


    document.getElementById(
        "primaryDistance"
    ).textContent =

        first
            ? first.distance + " km"
            : "";


    document.getElementById(
        "secondaryName"
    ).textContent =

        second
            ? second.name
            : "Nėra";


    document.getElementById(
        "secondaryDistance"
    ).textContent =

        second
            ? second.distance + " km"
            : "";


    document.getElementById(
        "tertiaryName"
    ).textContent =

        third
            ? third.name
            : "Nėra";


    document.getElementById(
        "tertiaryDistance"
    ).textContent =

        third
            ? third.distance + " km"
            : "";


    document.getElementById(
        "status"
    ).textContent =
        message;

}


// Rodome kitas vėjo stotis

function displayWindStations(
    stations,
    first,
    second,
    third
) {

    if (!isWindOnlyEnabled()) {

        return;

    }


    const selectedCodes =
        new Set();


    if (first) {

        selectedCodes.add(
            first.code
        );

    }


    if (second) {

        selectedCodes.add(
            second.code
        );

    }


    if (third) {

        selectedCodes.add(
            third.code
        );

    }


    stations.forEach(

        station => {

            if (
                selectedCodes.has(
                    station.code
                )
            ) {

                return;

            }


            const marker =
                L.marker(

                    [
                        station.latitude,
                        station.longitude
                    ],

                    {
                        icon:
                            windStationIcon
                    }

                ).addTo(map);


            marker.bindPopup(

                "<b>" +
                escapeHtml(
                    station.name
                ) +
                "</b>" +

                "<br>Kodas: " +

                escapeHtml(
                    station.code
                ) +

                "<br>Atstumas: " +

                station.distance +

                " km"

            );


            windStationMarkers.push(
                marker
            );

        }

    );

}


// Rodome pasirinktas stotis

function displayStations(
    latitude,
    longitude,
    first,
    second,
    third,
    locationName,
    mapStations
) {

    clearMapObjects();


    currentLocation = {

        latitude:
            latitude,

        longitude:
            longitude

    };


    currentNearest =
        first;

    currentSecond =
        second;

    currentThird =
        third;


    document.getElementById(
        "zoomButton"
    ).disabled = false;


    // Pasirinkta vieta

    locationMarker =
        L.marker(

            [
                latitude,
                longitude
            ],

            {
                icon:
                    locationIcon
            }

        ).addTo(map);


    locationMarker.bindPopup(

        "<b>Pasirinkta vieta</b>" +

        "<br>" +

        escapeHtml(
            locationName
        )

    );


    // Pirma stotis

    if (first) {

        nearestMarker =
            L.marker(

                [
                    first.latitude,
                    first.longitude
                ],

                {
                    icon:
                        nearestIcon
                }

            ).addTo(map);


        nearestMarker.bindPopup(

            "<b>Artimiausia stotis</b>" +

            "<br>" +

            escapeHtml(
                first.name
            ) +

            "<br>Kodas: " +

            escapeHtml(
                first.code
            ) +

            "<br>Atstumas: " +

            first.distance +

            " km"

        );


        nearestLine =
            L.polyline(

                [

                    [
                        latitude,
                        longitude
                    ],

                    [
                        first.latitude,
                        first.longitude
                    ]

                ],

                {
                    color:
                        "#d94a45",

                    weight:
                        3
                }

            ).addTo(map);

    }


    // Antra stotis

    if (second) {

        secondNearestMarker =
            L.marker(

                [
                    second.latitude,
                    second.longitude
                ],

                {
                    icon:
                        secondNearestIcon
                }

            ).addTo(map);


        secondNearestMarker.bindPopup(

            "<b>Antroji stotis</b>" +

            "<br>" +

            escapeHtml(
                second.name
            ) +

            "<br>Kodas: " +

            escapeHtml(
                second.code
            ) +

            "<br>Atstumas: " +

            second.distance +

            " km"

        );


        secondNearestLine =
            L.polyline(

                [

                    [
                        latitude,
                        longitude
                    ],

                    [
                        second.latitude,
                        second.longitude
                    ]

                ],

                {
                    color:
                        "#ed9d2f",

                    weight:
                        3,

                    dashArray:
                        "8,8"
                }

            ).addTo(map);

    }


    // Trečia stotis

    if (third) {

        thirdNearestMarker =
            L.marker(

                [
                    third.latitude,
                    third.longitude
                ],

                {
                    icon:
                        thirdNearestIcon
                }

            ).addTo(map);


        thirdNearestMarker.bindPopup(

            "<b>Trečioji stotis</b>" +

            "<br>" +

            escapeHtml(
                third.name
            ) +

            "<br>Kodas: " +

            escapeHtml(
                third.code
            ) +

            "<br>Atstumas: " +

            third.distance +

            " km"

        );


        thirdNearestLine =
            L.polyline(

                [

                    [
                        latitude,
                        longitude
                    ],

                    [
                        third.latitude,
                        third.longitude
                    ]

                ],

                {
                    color:
                        "#c7ae00",

                    weight:
                        3,

                    dashArray:
                        "3,8"
                }

            ).addTo(map);

    }


    displayWindStations(

        mapStations || [],

        first,

        second,

        third

    );

}


// Ieškome stočių pagal koordinates

async function findStations(
    latitude,
    longitude,
    locationName
) {

    document.getElementById(
        "status"
    ).textContent =
        "Ieškomos artimiausios stotys...";


    try {

        const response =
            await fetch(

                "/api/stations",

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            latitude:
                                latitude,

                            longitude:
                                longitude,

                            wind_only:
                                isWindOnlyEnabled()

                        })

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            throw new Error(

                result.error ||
                "Nepavyko gauti stočių."

            );

        }


        updateResults(

            result.primary,

            result.secondary,

            result.tertiary,

            isWindOnlyEnabled()

                ? "Rodomos tik vėjo duomenis teikiančios stotys"

                : "Rodomos artimiausios stotys"

        );


        displayStations(

            latitude,

            longitude,

            result.primary,

            result.secondary,

            result.tertiary,

            locationName,

            result.map_stations

        );


    }

    catch (error) {

        console.error(

            "Stočių paieškos klaida:",

            error

        );


        document.getElementById(
            "status"
        ).textContent =
            error.message;

    }

}


// Išvalome vietovių pasiūlymus

function clearAutocomplete() {

    const container =
        document.getElementById(
            "autocompleteResults"
        );


    container.innerHTML = "";

    container.style.display =
        "none";


    autocompleteResults = [];

}


// Rodome paieškos laukimą

function showAutocompleteLoading() {

    const container =
        document.getElementById(
            "autocompleteResults"
        );


    container.innerHTML =

        '<div class="autocomplete-loading">' +

        "Ieškoma..." +

        "</div>";


    container.style.display =
        "block";

}


// Rodome vietovių pasiūlymus

function displayAutocompleteResults(
    results
) {

    const container =
        document.getElementById(
            "autocompleteResults"
        );


    container.innerHTML = "";

    autocompleteResults =
        results;


    if (!results.length) {

        container.style.display =
            "none";

        return;

    }


    results.forEach(

        (result, index) => {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "autocomplete-item";


            item.innerHTML =

                '<div class="autocomplete-name">' +

                escapeHtml(
                    result.name
                ) +

                "</div>" +

                '<div class="autocomplete-address">' +

                escapeHtml(
                    result.formatted
                ) +

                "</div>";


            item.addEventListener(

                "mousedown",

                function(event) {

                    event.preventDefault();

                    selectAutocompleteResult(
                        index
                    );

                }

            );


            container.appendChild(
                item
            );

        }

    );


    container.style.display =
        "block";

}


// Pasirenkame vietovę

function selectAutocompleteResult(
    index
) {

    const result =
        autocompleteResults[index];


    if (!result) {

        return;

    }


    const input =
        document.getElementById(
            "locationInput"
        );


    input.value =
        result.formatted;


    clearAutocomplete();


    // Koordinates jau gautos iš Geoapify

    findStations(

        result.latitude,

        result.longitude,

        result.formatted

    );

}


// Vietovių pasiūlymų užklausa

async function requestAutocomplete(
    text
) {

    if (autocompleteController) {

        autocompleteController.abort();

    }


    autocompleteController =
        new AbortController();


    showAutocompleteLoading();


    try {

        const response =
            await fetch(

                "/api/autocomplete?text=" +

                encodeURIComponent(
                    text
                ),

                {

                    method:
                        "GET",

                    signal:
                        autocompleteController.signal

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            clearAutocomplete();

            return;

        }


        displayAutocompleteResults(

            result.results

        );


    }

    catch (error) {

        if (
            error.name !==
            "AbortError"
        ) {

            console.error(

                "Vietovių paieškos klaida:",

                error

            );


            clearAutocomplete();

        }

    }

}


// Paieškos laukelio įvestis

document
    .getElementById(
        "locationInput"
    )
    .addEventListener(

        "input",

        function() {

            const text =
                this.value.trim();


            clearTimeout(
                autocompleteTimer
            );


            if (text.length < 2) {

                clearAutocomplete();

                return;

            }


            autocompleteTimer =
                setTimeout(

                    function() {

                        requestAutocomplete(
                            text
                        );

                    },

                    300

                );

        }

    );


// Paieška paspaudus Enter

document
    .getElementById(
        "locationInput"
    )
    .addEventListener(

        "keydown",

        function(event) {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                clearAutocomplete();

                searchLocation();

            }

        }

    );


// Paieškos mygtukas

document
    .getElementById(
        "findButton"
    )
    .addEventListener(

        "click",

        function() {

            clearAutocomplete();

            searchLocation();

        }

    );


// Ieškome įvestos vietovės

async function searchLocation() {

    const input =
        document.getElementById(
            "locationInput"
        );


    const button =
        document.getElementById(
            "findButton"
        );


    const location =
        input.value.trim();


    if (!location) {

        document.getElementById(
            "status"
        ).textContent =
            "Įveskite vietovę.";

        input.focus();

        return;

    }


    button.disabled =
        true;

    button.textContent =
        "Ieškoma...";


    document.getElementById(
        "status"
    ).textContent =
        "Ieškoma vietovės...";


    try {

        const response =
            await fetch(

                "/api/location",

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            location:
                                location

                        })

                }

            );


        const result =
            await response.json();


        if (
            !response.ok ||
            !result.success
        ) {

            throw new Error(

                result.error ||
                "Vietovė nerasta."

            );

        }


        await findStations(

            result.latitude,

            result.longitude,

            result.name

        );


    }

    catch (error) {

        console.error(

            "Vietovės paieškos klaida:",

            error

        );


        document.getElementById(
            "status"
        ).textContent =
            error.message;

    }


    finally {

        button.disabled =
            false;

        button.textContent =
            "Ieškoti";

    }

}


// Uždaryti pasiūlymus paspaudus kitur

document.addEventListener(

    "click",

    function(event) {

        const searchBox =
            document.querySelector(
                ".autocomplete-wrapper"
            );


        if (
            !searchBox.contains(
                event.target
            )
        ) {

            clearAutocomplete();

        }

    }

);


// Paieška paspaudus žemėlapį

map.on(

    "click",

    async function(event) {

        const latitude =
            event.latlng.lat;


        const longitude =
            event.latlng.lng;


        clearAutocomplete();


        await findStations(

            latitude,

            longitude,

            "Žemėlapyje pasirinkta vieta"

        );

    }

);


// Vėjo filtravimas

document
    .getElementById(
        "windOnly"
    )
    .addEventListener(

        "change",

        async function() {

            if (!currentLocation) {

                return;

            }


            await findStations(

                currentLocation.latitude,

                currentLocation.longitude,

                "Žemėlapyje pasirinkta vieta"

            );

        }

    );


// Priartinimo mygtukas

document
    .getElementById(
        "zoomButton"
    )
    .addEventListener(

        "click",

        function() {

            if (
                !currentLocation ||
                !currentNearest
            ) {

                return;

            }


            const points = [

                [
                    currentLocation.latitude,
                    currentLocation.longitude
                ],

                [
                    currentNearest.latitude,
                    currentNearest.longitude
                ]

            ];


            if (currentSecond) {

                points.push([

                    currentSecond.latitude,
                    currentSecond.longitude

                ]);

            }


            if (currentThird) {

                points.push([

                    currentThird.latitude,
                    currentThird.longitude

                ]);

            }


            const bounds =
                L.latLngBounds(
                    points
                );


            map.fitBounds(

                bounds,

                {
                    padding:
                        [70, 70]
                }

            );

        }

    );


// Užtikriname tinkamą žemėlapio dydį

setTimeout(

    function() {

        map.invalidateSize();

    },

    300

);
