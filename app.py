from flask import Flask, render_template, request, jsonify
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


app = Flask(__name__)


# ============================================================
# METEO.LT API
# ============================================================

STATIONS_API = "https://api.meteo.lt/v1/stations"


# ============================================================
# STATIONS THAT PROVIDE WIND DATA
# ============================================================

WIND_STATIONS = {

    "birzu-ams",
    "dotnuvos-ams",
    "duksto-ams",
    "kauno-ams",
    "klaipedos-ams",
    "kybartu-ams",
    "laukuvos-ams",
    "lazdiju-ams",
    "marijampoles-ams",
    "mazeikiu-ams",
    "nidos-ams",
    "panevezio-ams",
    "raseiniu-ams",
    "rokiskio-ams",
    "siauliu-ams",
    "silutes-ams",
    "svencioniu-ams",
    "taurages-ams",
    "telsiu-ams",
    "ukmerges-ams",
    "utenos-ams",
    "varenos-ams",
    "ventes-ams",
    "vezaiciu-ams",
    "vilniaus-ams"

}


# ============================================================
# MANUAL STATIONS
# ============================================================

MANUAL_STATIONS = [

    {
        "code": "SUMSKO_AMS",
        "name": "Šumsko AMS",
        "latitude": 54.560519,
        "longitude": 25.720027,
        "wind_capable": True
    },

    {
        "code": "VILNIAUS_AS",
        "name": "Vilniaus AS",
        "latitude": 54.640950,
        "longitude": 25.292500,
        "wind_capable": True
    },

    {
        "code": "KAUNO_AS",
        "name": "Kauno AS",
        "latitude": 54.964220,
        "longitude": 24.069040,
        "wind_capable": True
    },

    {
        "code": "PALANGOS_AS",
        "name": "Palangos AS",
        "latitude": 55.979480,
        "longitude": 21.094110,
        "wind_capable": True
    },

    {
        "code": "KLAIPEDOS_JURU_UOSTAS",
        "name": "Klaipėdos jūrų uostas",
        "latitude": 55.664820,
        "longitude": 21.149590,
        "wind_capable": True
    },

    {
        "code": "KLAIPEDOS_BOKSTAS",
        "name": "Klaipėdos bokštas",
        "latitude": 55.731342,
        "longitude": 21.091502,
        "wind_capable": True
    },

    {
        "code": "NIDA_JURA",
        "name": "Nida (jūra)",
        "latitude": 55.2808252,
        "longitude": 20.9557657,
        "wind_capable": True
    },

    {
        "code": "VILNIAUS_LHMT_AMS",
        "name": "Vilniaus (LHMT) AMS",
        "latitude": 54.701333,
        "longitude": 25.271500,
        "wind_capable": True
    }

]


# ============================================================
# LOAD STATIONS
# ============================================================

def load_stations():

    stations = []

    try:

        response = requests.get(
            STATIONS_API,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()


        for station in data:

            coordinates = station.get(
                "coordinates",
                {}
            )

            latitude = coordinates.get(
                "latitude"
            )

            longitude = coordinates.get(
                "longitude"
            )

            if latitude is None or longitude is None:
                continue


            code = station.get(
                "code",
                ""
            )

            name = station.get(
                "name",
                "Nežinoma stotis"
            )


            wind_capable = (
                code.lower()
                in WIND_STATIONS
            )


            stations.append({

                "code": code,

                "name": name,

                "latitude": float(latitude),

                "longitude": float(longitude),

                "wind_capable": wind_capable

            })


    except Exception as error:

        print(
            f"Nepavyko įkelti Meteo.lt stočių: {error}"
        )


    # Add manual stations

    stations.extend(
        MANUAL_STATIONS
    )


    return stations


# ============================================================
# FIND NEAREST STATIONS
# ============================================================

def calculate_nearest_stations(
    latitude,
    longitude,
    wind_only=False
):

    stations = load_stations()


    if not stations:

        return {

            "success": False,

            "error":
                "Nepavyko įkelti meteorologijos stočių."

        }


    # ========================================================
    # FILTER
    # ========================================================

    if wind_only:

        stations = [

            station

            for station in stations

            if station.get(
                "wind_capable",
                False
            )

        ]


    if not stations:

        return {

            "success": False,

            "error":
                "Nerasta stočių, teikiančių vėjo duomenis."

        }


    # ========================================================
    # DISTANCES
    # ========================================================

    user_coordinates = (
        latitude,
        longitude
    )


    stations_with_distance = []


    for station in stations:

        station_coordinates = (

            station["latitude"],

            station["longitude"]

        )


        distance = geodesic(

            user_coordinates,

            station_coordinates

        ).km


        stations_with_distance.append({

            "code":
                station["code"],

            "name":
                station["name"],

            "latitude":
                station["latitude"],

            "longitude":
                station["longitude"],

            "distance":
                round(
                    distance,
                    2
                ),

            "wind_capable":
                station.get(
                    "wind_capable",
                    False
                )

        })


    # ========================================================
    # SORT
    # ========================================================

    stations_with_distance.sort(

        key=lambda station:
            station["distance"]

    )


    # ========================================================
    # RETURN THREE
    # ========================================================

    return {

        "success": True,

        "primary":
            stations_with_distance[0]
            if len(stations_with_distance) > 0
            else None,

        "secondary":
            stations_with_distance[1]
            if len(stations_with_distance) > 1
            else None,

        "tertiary":
            stations_with_distance[2]
            if len(stations_with_distance) > 2
            else None

    }


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# SEARCH LOCATION
# ============================================================

@app.route(
    "/api/location",
    methods=["POST"]
)
def location():

    data = request.get_json()

    location_text = data.get(
        "location",
        ""
    ).strip()


    if not location_text:

        return jsonify({

            "success": False,

            "error":
                "Įveskite vietovę."

        })


    try:

        geolocator = Nominatim(

            user_agent=
                "meteorologines-stoties-paieska"

        )


        location = geolocator.geocode(

            location_text

        )


        if location is None:

            return jsonify({

                "success": False,

                "error":
                    "Vietovė nerasta."

            })


        return jsonify({

            "success": True,

            "name":
                location.address,

            "latitude":
                location.latitude,

            "longitude":
                location.longitude

        })


    except Exception as error:

        return jsonify({

            "success": False,

            "error":
                str(error)

        })


# ============================================================
# FIND STATIONS
# ============================================================

@app.route(
    "/api/stations",
    methods=["POST"]
)
def stations():

    data = request.get_json()


    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )

    wind_only = data.get(
        "wind_only",
        False
    )


    if latitude is None or longitude is None:

        return jsonify({

            "success": False,

            "error":
                "Trūksta koordinačių."

        })


    result = calculate_nearest_stations(

        float(latitude),

        float(longitude),

        bool(wind_only)

    )


    return jsonify(result)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )