from flask import Flask, render_template, request, jsonify
import requests
from geopy.distance import geodesic
from datetime import datetime, timedelta
from threading import Lock
import os
import time


app = Flask(__name__)


# Nustatymai

STATIONS_API = "https://api.meteo.lt/v1/stations"

GEOCODING_API = (
    "https://api.geoapify.com/v1/geocode/autocomplete"
)

GEOCODING_SEARCH_API = (
    "https://api.geoapify.com/v1/geocode/search"
)

GEOAPIFY_API_KEY = os.environ.get(
    "GEOAPIFY_API_KEY"
)

UPDATE_INTERVAL = timedelta(
    minutes=15
)

REQUEST_LIMIT = 60

REQUEST_PERIOD = 60


# Stotys su vėjo duomenim

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


# stations kuriu nera meteo API

ADDITIONAL_STATIONS = [

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
        "wind_capable": False
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
        "wind_capable": False
    }

]


# Stočių talpykla

stations_cache = {
    "stations": None,
    "timestamp": None
}

stations_cache_lock = Lock()


# Vietovių paieškos talpykla

location_cache = {}

location_cache_lock = Lock()


# Užklausų ribojimas

request_history = {}

request_lock = Lock()


def check_rate_limit():

    address = request.remote_addr or "nežinomas"

    now = time.time()

    with request_lock:

        timestamps = request_history.get(
            address,
            []
        )

        timestamps = [

            timestamp

            for timestamp in timestamps

            if now - timestamp
            < REQUEST_PERIOD

        ]

        if len(timestamps) >= REQUEST_LIMIT:

            request_history[address] = timestamps

            return False

        timestamps.append(now)

        request_history[address] = timestamps

    return True


def load_stations():

    now = datetime.utcnow()

    # Tikriname talpyklą

    with stations_cache_lock:

        if (

            stations_cache["stations"] is not None

            and stations_cache["timestamp"] is not None

            and now - stations_cache["timestamp"]
            < UPDATE_INTERVAL

        ):

            return stations_cache["stations"]


    try:

        atsakymas = requests.get(

            STATIONS_API,

            timeout=15,

            headers={

                "User-Agent":
                    "MeteorologijosStociuPaieska/1.0"

            }

        )

        atsakymas.raise_for_status()

        data = atsakymas.json()

        stations = []


        for stotis in data:

            coordinates = stotis.get(
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


            code = stotis.get(
                "code",
                ""
            )

            name = stotis.get(
                "name",
                "Nežinoma stotis"
            )


            wind_capable = (

                code.lower()

                in WIND_STATIONS

            )


            stations.append({

                "code":
                    code,

                "name":
                    name,

                "latitude":
                    float(latitude),

                "longitude":
                    float(longitude),

                "wind_capable":
                    wind_capable

            })

        stations.extend(
            ADDITIONAL_STATIONS
        )


        # Išsaugome talpykloje

        with stations_cache_lock:

            stations_cache["stations"] = stations

            stations_cache["timestamp"] = now


        return stations


    except Exception as error:

        print(
            f"Stočių įkėlimo error: {error}"
        )


        with stations_cache_lock:

            if stations_cache["stations"] is not None:

                return stations_cache["stations"]


        return ADDITIONAL_STATIONS.copy()


def find_nearest_stations(

    latitude,

    longitude,

    wind_only=False

):

    stations = load_stations()


    # Jei įjungtas vėjo filtras

    if wind_only:

        stations = [

            stotis

            for stotis in stations

            if stotis.get(
                "wind_capable",
                False
            )

        ]


    if not stations:

        return {

            "success": False,

            "error":
                "Nerasta tinkamų meteorologijos stočių."

        }


    location_coords = (

        latitude,

        longitude

    )


    stations_with_distance = []


    for stotis in stations:

        station_coords = (

            stotis["latitude"],

            stotis["longitude"]

        )


        distance = geodesic(

            location_coords,

            station_coords

        ).km


        stations_with_distance.append({

            "code":
                stotis["code"],

            "name":
                stotis["name"],

            "latitude":
                stotis["latitude"],

            "longitude":
                stotis["longitude"],

            "distance":
                round(
                    distance,
                    2
                ),

            "wind_capable":
                stotis.get(
                    "wind_capable",
                    False
                )

        })


    # pagal atstumą

    stations_with_distance.sort(

        key=lambda stotis:
            stotis["distance"]

    )


    first_station = (

        stations_with_distance[0]

        if len(stations_with_distance) >= 1

        else None

    )


    second_station = (

        stations_with_distance[1]

        if len(stations_with_distance) >= 2

        else None

    )


    third_station = (

        stations_with_distance[2]

        if len(stations_with_distance) >= 3

        else None

    )


    # visos vėjo stotis žemėlapyje

    if wind_only:

        map_stations = stations_with_distance

    else:

        map_stations = []


    return {

        "success": True,

        "primary":
            first_station,

        "secondary":
            second_station,

        "tertiary":
            third_station,

        "map_stations":
            map_stations

    }


@app.route("/")
def main_page():

    return render_template(
        "index.html"
    )


@app.route(
    "/api/autocomplete",
    methods=["GET"]
)
def location_suggestions():

    if not check_rate_limit():

        return jsonify({

            "success": False,

            "error":
                "Per daug užklausų. Palaukite minutę."

        }), 429


    text = request.args.get(
        "text",
        ""
    ).strip()


    if len(text) < 2:

        return jsonify({

            "success": True,

            "results": []

        })


    if not GEOAPIFY_API_KEY:

        print(
            "Klaida: GEOAPIFY_API_KEY nesukonfigūruotas."
        )


        return jsonify({

            "success": False,

            "error":
                "Geokodavimo API nesukonfigūruotas."

        }), 500


    cache_key = text.lower()


    with location_cache_lock:

        cached = location_cache.get(
            cache_key
        )


    if cached is not None:

        return jsonify({

            "success": True,

            "results":
                cached

        })


    try:

        atsakymas = requests.get(

            GEOCODING_API,

            params={

                "text":
                    text,

                "apiKey":
                    GEOAPIFY_API_KEY,

                "format":
                    "json",

                "limit":
                    5,

                "filter":
                    "countrycode:lt",

                "lang":
                    "lt"

            },

            timeout=8

        )


        if atsakymas.status_code == 401:

            return jsonify({

                "success": False,

                "error":
                    "Geokodavimo API raktas neteisingas."

            }), 500


        if atsakymas.status_code == 429:

            return jsonify({

                "success": False,

                "error":
                    "Pasiektas vietovių paieškos limitas."

            }), 429


        atsakymas.raise_for_status()

        data = atsakymas.json()

        results = []


        for result in data.get(
            "results",
            []
        ):

            latitude = result.get(
                "lat"
            )

            longitude = result.get(
                "lon"
            )


            if latitude is None or longitude is None:

                continue


            name = result.get(
                "name"
            )


            address = result.get(
                "formatted"
            )


            if not name:

                name = (

                    address
                    or
                    "Nežinoma location_coords"

                )


            if not address:

                address = name


            results.append({

                "name":
                    name,

                "formatted":
                    address,

                "latitude":
                    float(latitude),

                "longitude":
                    float(longitude)

            })


        with location_cache_lock:

            location_cache[
                cache_key
            ] = results


        return jsonify({

            "success": True,

            "results":
                results

        })


    except requests.exceptions.RequestException as error:

        print(
            f"Geokodavimo error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Nepavyko atlikti vietovės paieškos."

        }), 503


    except Exception as error:

        print(
            f"Vietovių paieškos error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Įvyko vietovės paieškos error."

        }), 500


@app.route(
    "/api/location",
    methods=["POST"]
)
def search_location():

    if not check_rate_limit():

        return jsonify({

            "success": False,

            "error":
                "Per daug užklausų. Palaukite minutę."

        }), 429


    data = request.get_json(
        silent=True
    ) or {}


    location = str(
        data.get(
            "location",
            ""
        )
    ).strip()


    if not location:

        return jsonify({

            "success": False,

            "error":
                "Įveskite vietovę."

        }), 400


    if not GEOAPIFY_API_KEY:

        return jsonify({

            "success": False,

            "error":
                "Geokodavimo API nesukonfigūruotas."

        }), 500


    try:

        atsakymas = requests.get(

            GEOCODING_SEARCH_API,

            params={

                "text":
                    location,

                "apiKey":
                    GEOAPIFY_API_KEY,

                "format":
                    "json",

                "limit":
                    1,

                "filter":
                    "countrycode:lt",

                "lang":
                    "lt"

            },

            timeout=8

        )


        if atsakymas.status_code == 401:

            return jsonify({

                "success": False,

                "error":
                    "Geokodavimo API raktas neteisingas."

            }), 500


        if atsakymas.status_code == 429:

            return jsonify({

                "success": False,

                "error":
                    "Pasiektas vietovių paieškos limitas."

            }), 429


        atsakymas.raise_for_status()

        data = atsakymas.json()

        results = data.get(
            "results",
            []
        )


        if not results:

            return jsonify({

                "success": False,

                "error":
                    f"Vietovė „{location}“ nerasta."

            }), 404


        result = results[0]


        latitude = result.get(
            "lat"
        )

        longitude = result.get(
            "lon"
        )


        if latitude is None or longitude is None:

            return jsonify({

                "success": False,

                "error":
                    "Vietovei nepavyko nustatyti koordinačių."

            }), 404


        return jsonify({

            "success": True,

            "name":
                result.get(
                    "formatted",
                    location
                ),

            "latitude":
                float(latitude),

            "longitude":
                float(longitude)

        })


    except Exception as error:

        print(
            f"Vietovės paieškos error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Nepavyko atlikti vietovės paieškos."

        }), 503


@app.route(
    "/api/stations",
    methods=["POST"]
)
def station_search():

    if not check_rate_limit():

        return jsonify({

            "success": False,

            "error":
                "Per daug užklausų. Palaukite minutę."

        }), 429


    data = request.get_json(
        silent=True
    ) or {}


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


    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "error":
                "Neteisingos coordinates."

        }), 400


    if not -90 <= latitude <= 90:

        return jsonify({

            "success": False,

            "error":
                "Neteisinga latitude."

        }), 400


    if not -180 <= longitude <= 180:

        return jsonify({

            "success": False,

            "error":
                "Neteisinga longitude."

        }), 400


    result = find_nearest_stations(

        latitude,

        longitude,

        bool(wind_only)

    )


    return jsonify(
        result
    )


@app.route("/health")
def health_check():

    return jsonify({

        "status":
            "ok"

    })


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
