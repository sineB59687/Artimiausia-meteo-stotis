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
// CURRENT MAP OBJECTS
// ============================================================

let userMarker = null;

let primaryMarker = null;

let secondaryMarker = null;

let tertiaryMarker = null;


let primaryLine = null;

let secondaryLine = null;

let tertiaryLine = null;


// ============================================================
// CURRENT LOCATIONS
// ============================================================

let currentUserLocation = null;

let currentPrimary = null;

let currentSecondary = null;

let currentTertiary = null;


// ============================================================
// FILTER
// ============================================================

function windOnlyEnabled() {

    return document.getElementById(
        "windOnly"
    ).checked;

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


    userMarker = null;

    primaryMarker = null;

    secondaryMarker = null;

    tertiaryMarker = null;

    primaryLine = null;

    secondaryLine = null;

    tertiaryLine = null;

}


// ============================================================
// UPDATE RESULTS
// ============================================================

function updateResults(

    primary,
    secondary,
    tertiary,
    statusText

) {


    // Primary

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


    // Secondary

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


    // Tertiary

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
// DISPLAY STATIONS
// ============================================================

function displayStations(

    latitude,
    longitude,
    primary,
    secondary,
    tertiary,
    locationName

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
    // SELECTED LOCATION
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

        "<b>Pasirinkta vieta</b><br>"
        + locationName

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

                    radius: 9,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#d9534f",

                    fillOpacity: 1

                }

            ).addTo(map);


        primaryMarker.bindPopup(

            "<b>Pagrindinė stotis</b><br>"
            + primary.name
            + "<br>Kodas: "
            + primary.code
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

                    color:
                        "#d9534f",

                    weight:
                        3

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

                    radius: 8,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#f0ad4e",

                    fillOpacity: 1

                }

            ).addTo(map);


        secondaryMarker.bindPopup(

            "<b>Antroji stotis</b><br>"
            + secondary.name
            + "<br>Kodas: "
            + secondary.code
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

                    color:
                        "#f0ad4e",

                    weight:
                        3,

                    dashArray:
                        "8, 8"

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

                    radius: 8,

                    color: "#ffffff",

                    weight: 2,

                    fillColor: "#f7d154",

                    fillOpacity: 1

                }

            ).addTo(map);


        tertiaryMarker.bindPopup(

            "<b>Trečioji stotis</b><br>"
            + tertiary.name
            + "<br>Kodas: "
            + tertiary.code
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

                    color:
                        "#f7d154",

                    weight:
                        3,

                    dashArray:
                        "3, 8"

                }

            ).addTo(map);

    }

}


// ============================================================
// SEARCH LOCATION
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

        return;

    }


    button.disabled = true;

    button.textContent =
        "Ieškoma...";


    document.getElementById(
        "status"
    ).textContent =
        "Ieškoma vietovės...";


    try {


        // ====================================================
        // GEOCODING
        // ====================================================

        const locationResponse =
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


        const locationResult =
            await locationResponse.json();


        if (!locationResult.success) {

            document.getElementById(
                "status"
            ).textContent =
                locationResult.error;

            return;

        }


        // ====================================================
        // FIND STATIONS
        // ====================================================

        await findStations(

            locationResult.latitude,

            locationResult.longitude,

            locationResult.name

        );


    }


    catch (error) {

        console.error(error);

        document.getElementById(
            "status"
        ).textContent =
            "Įvyko klaida.";

    }


    finally {

        button.disabled =
            false;

        button.textContent =
            "Ieškoti stočių";

    }

}


// ============================================================
// FIND STATIONS
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
                                windOnlyEnabled()

                        })

                }

            );


        const result =
            await response.json();


        if (!result.success) {

            document.getElementById(
                "status"
            ).textContent =
                result.error;

            return;

        }


        updateResults(

            result.primary,

            result.secondary,

            result.tertiary,

            windOnlyEnabled()

                ? "Rodomos tik vėjo duomenis teikiančios stotys"

                : "Vieta rasta"

        );


        displayStations(

            latitude,

            longitude,

            result.primary,

            result.secondary,

            result.tertiary,

            locationName

        );

    }


    catch (error) {

        console.error(error);

        document.getElementById(
            "status"
        ).textContent =
            "Nepavyko gauti stočių duomenų.";

    }

}


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
// SEARCH BUTTON
// ============================================================

document
    .getElementById(
        "findButton"
    )
    .addEventListener(

        "click",

        searchLocation

    );


// ============================================================
// ENTER KEY
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

                searchLocation();

            }

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
                L.latLngBounds(points);


            map.fitBounds(

                bounds,

                {

                    padding:
                        [50, 50]

                }

            );

        }

    );