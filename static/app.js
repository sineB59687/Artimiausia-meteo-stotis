// ============================================================
// MAP
// ============================================================

const map = L.map(
    "map"
).setView(

    [55.1694, 23.8813],

    7

);


L.tileLayer(

    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

    {

        maxZoom: 19,

        attribution:
            "&copy; OpenStreetMap contributors"

    }

).addTo(map);


// ============================================================
// MAP OBJECTS
// ============================================================

let userMarker = null;

let primaryMarker = null;

let secondaryMarker = null;

let tertiaryMarker = null;


let primaryLine = null;

let secondaryLine = null;

let tertiaryLine = null;


let windStationMarkers = [];


// ============================================================
// CURRENT DATA
// ============================================================

let currentUserLocation = null;

let currentPrimary = null;

let currentSecondary = null;

let currentTertiary = null;


// ============================================================
// AUTOCOMPLETE
// ============================================================

let autocompleteTimer = null;

let autocompleteController = null;

let autocompleteResults = [];


// ============================================================
// FILTER
// ============================================================

function windOnlyEnabled() {

    return document.getElementById(
        "windOnly"
    ).checked;

}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;

}


// ============================================================
// CLEAR MAP
// ============================================================

function clearMapObjects() {


    const objects = [

        userMarker,

        primaryMarker,

        secondaryMarker,

        tertiaryMarker,

        primaryLine,

        secondaryLine,

        tertiaryLine

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


    userMarker = null;

    primaryMarker = null;

    secondaryMarker = null;

    tertiaryMarker = null;

    primaryLine = null;

    secondaryLine = null;

    tertiaryLine = null;

}


// ============================================================
// WIND STATION ICON
// ============================================================

const windStationIcon =
    L.divIcon({

        className: "",

        html:
            '<div class="wind-station-marker"></div>',

        iconSize: [12, 12],

        iconAnchor: [6, 6],

        popupAnchor: [0, -6]

    });


// ============================================================
// UPDATE RESULT CARDS
// ============================================================

function updateResults(

    primary,

    secondary,

    tertiary,

    statusText

) {


    document.getElementById(
        "primaryName"
    ).textContent =

        primary

            ? primary.name

            : "Nėra";


    document.getElementById(
        "primaryDistance"
    ).textContent =

        primary

            ? primary.distance + " km"

            : "";


    document.getElementById(
        "secondaryName"
    ).textContent =

        secondary

            ? secondary.name

            : "Nėra";


    document.getElementById(
        "secondaryDistance"
    ).textContent =

        secondary

            ? secondary.distance + " km"

            : "";


    document.getElementById(
        "tertiaryName"
    ).textContent =

        tertiary

            ? tertiary.name

            : "Nėra";


    document.getElementById(
        "tertiaryDistance"
    ).textContent =

        tertiary

            ? tertiary.distance + " km"

            : "";


    document.getElementById(
        "status"
    ).textContent =
        statusText;

}


// ============================================================
// DISPLAY WIND STATIONS
// ============================================================

function displayWindStations(

    stations,

    primary,

    secondary,

    tertiary

) {


    if (!windOnlyEnabled()) {

        return;

    }


    const selectedCodes =
        new Set();


    if (primary) {

        selectedCodes.add(
            primary.code
        );

    }


    if (secondary) {

        selectedCodes.add(
            secondary.code
        );

    }


    if (tertiary) {

        selectedCodes.add(
            tertiary.code
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

                "<b>"
                + escapeHtml(
                    station.name
                )
                + "</b>"
                + "<br>Kodas: "
                + escapeHtml(
                    station.code
                )
                + "<br>Atstumas: "
                + station.distance
                + " km"

            );


            windStationMarkers.push(
                marker
            );

        }

    );

}


// ============================================================
// DISPLAY SELECTED STATIONS
// ============================================================

function displayStations(

    latitude,

    longitude,

    primary,

    secondary,

    tertiary,

    locationName,

    mapStations

) {


    clearMapObjects();


    currentUserLocation = {

        latitude:
            latitude,

        longitude:
            longitude

    };


    currentPrimary =
        primary;

    currentSecondary =
        secondary;

    currentTertiary =
        tertiary;


    document.getElementById(
        "zoomButton"
    ).disabled = false;


    // ========================================================
    // USER LOCATION
    // ========================================================

    userMarker =
        L.circleMarker(

            [

                latitude,

                longitude

            ],

            {

                radius: 8,

                color: "#ffffff",

                weight: 2,

                fillColor: "#3578d4",

                fillOpacity: 1

            }

        ).addTo(map);


    userMarker.bindPopup(

        "<b>Pasirinkta vieta</b>"
        + "<br>"
        + escapeHtml(
            locationName
        )

    );


    // ========================================================
    // PRIMARY
    // ========================================================

    if (primary) {

        primaryMarker =
            L.circleMarker(

                [

                    primary.latitude,

                    primary.longitude

                ],

                {

                    radius: 10,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#d9534f",

                    fillOpacity: 1

                }

            ).addTo(map);


        primaryMarker.bindPopup(

            "<b>Pagrindinė stotis</b>"
            + "<br>"
            + escapeHtml(
                primary.name
            )
            + "<br>Kodas: "
            + escapeHtml(
                primary.code
            )
            + "<br>Atstumas: "
            + primary.distance
            + " km"

        );


        primaryLine =
            L.polyline(

                [

                    [

                        latitude,

                        longitude

                    ],

                    [

                        primary.latitude,

                        primary.longitude

                    ]

                ],

                {

                    color: "#d9534f",

                    weight: 3

                }

            ).addTo(map);

    }


    // ========================================================
    // SECONDARY
    // ========================================================

    if (secondary) {

        secondaryMarker =
            L.circleMarker(

                [

                    secondary.latitude,

                    secondary.longitude

                ],

                {

                    radius: 9,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#f0ad4e",

                    fillOpacity: 1

                }

            ).addTo(map);


        secondaryMarker.bindPopup(

            "<b>Antroji stotis</b>"
            + "<br>"
            + escapeHtml(
                secondary.name
            )
            + "<br>Kodas: "
            + escapeHtml(
                secondary.code
            )
            + "<br>Atstumas: "
            + secondary.distance
            + " km"

        );


        secondaryLine =
            L.polyline(

                [

                    [

                        latitude,

                        longitude

                    ],

                    [

                        secondary.latitude,

                        secondary.longitude

                    ]

                ],

                {

                    color: "#f0ad4e",

                    weight: 3,

                    dashArray: "8,8"

                }

            ).addTo(map);

    }


    // ========================================================
    // TERTIARY
    // ========================================================

    if (tertiary) {

        tertiaryMarker =
            L.circleMarker(

                [

                    tertiary.latitude,

                    tertiary.longitude

                ],

                {

                    radius: 9,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#f7d154",

                    fillOpacity: 1

                }

            ).addTo(map);


        tertiaryMarker.bindPopup(

            "<b>Trečioji stotis</b>"
            + "<br>"
            + escapeHtml(
                tertiary.name
            )
            + "<br>Kodas: "
            + escapeHtml(
                tertiary.code
            )
            + "<br>Atstumas: "
            + tertiary.distance
            + " km"

        );


        tertiaryLine =
            L.polyline(

                [

                    [

                        latitude,

                        longitude

                    ],

                    [

                        tertiary.latitude,

                        tertiary.longitude

                    ]

                ],

                {

                    color: "#f7d154",

                    weight: 3,

                    dashArray: "3,8"

                }

            ).addTo(map);

    }


    // ========================================================
    // ALL WIND STATIONS
    // ========================================================

    displayWindStations(

        mapStations || [],

        primary,

        secondary,

        tertiary

    );

}


// ============================================================
// FIND STATIONS FROM COORDINATES
// ============================================================

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

                    method: "POST",

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
                                windOnlyEnabled()

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

                result.error
                ||
                "Nepavyko gauti stočių."

            );

        }


        updateResults(

            result.primary,

            result.secondary,

            result.tertiary,

            windOnlyEnabled()

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
            "Station search error:",
            error
        );


        document.getElementById(
            "status"
        ).textContent =
            error.message;

    }

}


// ============================================================
// CLEAR AUTOCOMPLETE
// ============================================================

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


// ============================================================
// SHOW AUTOCOMPLETE LOADING
// ============================================================

function showAutocompleteLoading() {

    const container =
        document.getElementById(
            "autocompleteResults"
        );


    container.innerHTML =
        '<div class="autocomplete-loading">'
        + "Ieškoma..."
        + "</div>";


    container.style.display =
        "block";

}


// ============================================================
// DISPLAY AUTOCOMPLETE RESULTS
// ============================================================

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

                '<div class="autocomplete-name">'
                + escapeHtml(
                    result.name
                )
                + "</div>"

                +

                '<div class="autocomplete-address">'
                + escapeHtml(
                    result.formatted
                )
                + "</div>";


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


// ============================================================
// SELECT AUTOCOMPLETE RESULT
// ============================================================

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


    // ========================================================
    // IMPORTANT:
    // We already have coordinates.
    //
    // No second geocoding request is needed.
    // ========================================================

    findStations(

        result.latitude,

        result.longitude,

        result.formatted

    );

}


// ============================================================
// AUTOCOMPLETE SEARCH
// ============================================================

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

                "/api/autocomplete?text="
                +
                encodeURIComponent(
                    text
                ),

                {

                    method: "GET",

                    signal:
                        autocompleteController.signal

                }

            );


        const result =
            await response.json();


        if (!response.ok || !result.success) {

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
                "Autocomplete error:",
                error
            );

            clearAutocomplete();

        }

    }

}


// ============================================================
// INPUT EVENT
// ============================================================

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


            // Wait 300 ms after typing stops.

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


// ============================================================
// SEARCH BY ENTER
// ============================================================

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


// ============================================================
// SEARCH BUTTON
// ============================================================

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


// ============================================================
// DIRECT SEARCH
// ============================================================

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

                    method: "POST",

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

                result.error
                ||
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
            "Location search error:",
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
            "Ieškoti stočių";

    }

}


// ============================================================
// CLOSE AUTOCOMPLETE WHEN CLICKING OUTSIDE
// ============================================================

document.addEventListener(

    "click",

    function(event) {


        const wrapper =
            document.querySelector(
                ".autocomplete-wrapper"
            );


        if (
            !wrapper.contains(
                event.target
            )
        ) {

            clearAutocomplete();

        }

    }

);


// ============================================================
// MAP CLICK
// ============================================================

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


// ============================================================
// WIND FILTER
// ============================================================

document
    .getElementById(
        "windOnly"
    )
    .addEventListener(

        "change",

        async function() {


            if (!currentUserLocation) {

                return;

            }


            await findStations(

                currentUserLocation.latitude,

                currentUserLocation.longitude,

                "Žemėlapyje pasirinkta vieta"

            );

        }

    );


// ============================================================
// ZOOM BUTTON
// ============================================================

document
    .getElementById(
        "zoomButton"
    )
    .addEventListener(

        "click",

        function() {


            if (

                !currentUserLocation ||
                !currentPrimary

            ) {

                return;

            }


            const points = [

                [

                    currentUserLocation.latitude,

                    currentUserLocation.longitude

                ],

                [

                    currentPrimary.latitude,

                    currentPrimary.longitude

                ]

            ];


            if (currentSecondary) {

                points.push([

                    currentSecondary.latitude,

                    currentSecondary.longitude

                ]);

            }


            if (currentTertiary) {

                points.push([

                    currentTertiary.latitude,

                    currentTertiary.longitude

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
                        [60, 60]

                }

            );

        }

    );


// ============================================================
// FIX MAP SIZE
// ============================================================

setTimeout(

    function() {

        map.invalidateSize();

    },

    300

);
