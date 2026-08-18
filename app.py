from flask import Flask, render_template, request, jsonify
import requests
from geopy.distance import geodesic
from datetime import datetime, timedelta
from threading import Lock
import os
import time


app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

STATIONS_API = "https://api.meteo.lt/v1/stations"

GEOAPIFY_AUTOCOMPLETE_API = (
    "https://api.geoapify.com/v1/geocode/autocomplete"
)

GEOAPIFY_SEARCH_API = (
    "https://api.geoapify.com/v1/geocode/search"
)

GEOAPIFY_API_KEY = os.environ.get(
    "GEOAPIFY_API_KEY"
)

CACHE_DURATION = timedelta(minutes=15)

REQUEST_LIMIT = 60

REQUEST_WINDOW = 60


# ============================================================
# WIND-CAPABLE METEO.LT STATIONS
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
# MANUALLY ADDED STATIONS
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
# CACHES
# ============================================================

station_cache = {
    "stations": None,
    "timestamp": None
}

station_cache_lock = Lock()


autocomplete_cache = {}

autocomplete_cache_lock = Lock()


# ============================================================
# RATE LIMITING
# ============================================================

request_history = {}

rate_limit_lock = Lock()


def check_rate_limit():

    ip = request.remote_addr or "unknown"

    now = time.time()

    with rate_limit_lock:

        timestamps = request_history.get(
            ip,
            []
        )

        timestamps = [

            timestamp

            for timestamp in timestamps

            if now - timestamp < REQUEST_WINDOW

        ]

        if len(timestamps) >= REQUEST_LIMIT:

            request_history[ip] = timestamps

            return False

        timestamps.append(now)

        request_history[ip] = timestamps

    return True


# ============================================================
# LOAD STATIONS
# ============================================================

def load_stations():

    now = datetime.utcnow()

    # Check cache

    with station_cache_lock:

        if (

            station_cache["stations"] is not None

            and station_cache["timestamp"] is not None

            and now - station_cache["timestamp"]
            < CACHE_DURATION

        ):

            return station_cache["stations"]


    try:

        response = requests.get(

            STATIONS_API,

            timeout=15,

            headers={

                "User-Agent":
                    "ArtimiausiaMeteoStotis/1.0"

            }

        )

        response.raise_for_status()

        data = response.json()

        stations = []


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


        # Add manually entered stations

        stations.extend(
            MANUAL_STATIONS
        )


        # Save cache

        with station_cache_lock:

            station_cache["stations"] = stations

            station_cache["timestamp"] = now


        return stations


    except Exception as error:

        print(
            f"Meteo.lt station error: {error}"
        )


        # Use old cache if available

        with station_cache_lock:

            if station_cache["stations"] is not None:

                return station_cache["stations"]


        return MANUAL_STATIONS.copy()


# ============================================================
# FIND NEAREST STATIONS
# ============================================================

def calculate_nearest_stations(

    latitude,

    longitude,

    wind_only=False

):

    stations = load_stations()


    # Filter wind stations

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
                "Nerasta tinkamų meteorologijos stočių."

        }


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


    # Sort by distance

    stations_with_distance.sort(

        key=lambda station:
            station["distance"]

    )


    # Three nearest

    primary = (

        stations_with_distance[0]

        if len(stations_with_distance) >= 1

        else None

    )


    secondary = (

        stations_with_distance[1]

        if len(stations_with_distance) >= 2

        else None

    )


    tertiary = (

        stations_with_distance[2]

        if len(stations_with_distance) >= 3

        else None

    )


    # Other wind stations displayed on map

    if wind_only:

        map_stations = stations_with_distance

    else:

        map_stations = []


    return {

        "success": True,

        "primary":
            primary,

        "secondary":
            secondary,

        "tertiary":
            tertiary,

        "map_stations":
            map_stations

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
# GEOAPIFY AUTOCOMPLETE
# ============================================================

@app.route(
    "/api/autocomplete",
    methods=["GET"]
)
def autocomplete():

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
            "ERROR: GEOAPIFY_API_KEY is not configured."
        )


        return jsonify({

            "success": False,

            "error":
                "Geocoding API nėra sukonfigūruotas."

        }), 500


    # Check cache

    cache_key = text.lower()


    with autocomplete_cache_lock:

        cached = autocomplete_cache.get(
            cache_key
        )


    if cached is not None:

        return jsonify({

            "success": True,

            "results":
                cached

        })


    try:

        response = requests.get(

            GEOAPIFY_AUTOCOMPLETE_API,

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


        if response.status_code == 401:

            print(
                "Geoapify API key rejected."
            )


            return jsonify({

                "success": False,

                "error":
                    "Geocoding API raktas neteisingas."

            }), 500


        if response.status_code == 429:

            return jsonify({

                "success": False,

                "error":
                    "Pasiektas vietovės paieškos limitas."

            }), 429


        response.raise_for_status()

        data = response.json()

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


            formatted = result.get(
                "formatted"
            )


            if not name:

                name = (
                    formatted
                    or
                    "Nežinoma vieta"
                )


            if not formatted:

                formatted = name


            results.append({

                "name":
                    name,

                "formatted":
                    formatted,

                "latitude":
                    float(latitude),

                "longitude":
                    float(longitude)

            })


        # Save cache

        with autocomplete_cache_lock:

            autocomplete_cache[
                cache_key
            ] = results


        return jsonify({

            "success": True,

            "results":
                results

        })


    except requests.exceptions.RequestException as error:

        print(
            f"Geoapify request error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Nepavyko atlikti vietovės paieškos."

        }), 503


    except Exception as error:

        print(
            f"Autocomplete error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Įvyko vietovės paieškos klaida."

        }), 500


# ============================================================
# DIRECT LOCATION SEARCH
# ============================================================

@app.route(
    "/api/location",
    methods=["POST"]
)
def location():

    if not check_rate_limit():

        return jsonify({

            "success": False,

            "error":
                "Per daug užklausų. Palaukite minutę."

        }), 429


    data = request.get_json(
        silent=True
    ) or {}


    location_text = str(
        data.get(
            "location",
            ""
        )
    ).strip()


    if not location_text:

        return jsonify({

            "success": False,

            "error":
                "Įveskite vietovę."

        }), 400


    if not GEOAPIFY_API_KEY:

        return jsonify({

            "success": False,

            "error":
                "Geocoding API nėra sukonfigūruotas."

        }), 500


    try:

        response = requests.get(

            GEOAPIFY_SEARCH_API,

            params={

                "text":
                    location_text,

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


        if response.status_code == 401:

            return jsonify({

                "success": False,

                "error":
                    "Geocoding API raktas neteisingas."

            }), 500


        if response.status_code == 429:

            return jsonify({

                "success": False,

                "error":
                    "Pasiektas vietovės paieškos limitas."

            }), 429


        response.raise_for_status()

        data = response.json()

        results = data.get(
            "results",
            []
        )


        if not results:

            return jsonify({

                "success": False,

                "error":
                    f"Vietovė „{location_text}“ nerasta."

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
                    location_text
                ),

            "latitude":
                float(latitude),

            "longitude":
                float(longitude)

        })


    except Exception as error:

        print(
            f"Location search error: {error}"
        )


        return jsonify({

            "success": False,

            "error":
                "Nepavyko atlikti vietovės paieškos."

        }), 503


# ============================================================
# STATION SEARCH API
# ============================================================

@app.route(
    "/api/stations",
    methods=["POST"]
)
def stations():

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
                "Neteisingos koordinatės."

        }), 400


    if not -90 <= latitude <= 90:

        return jsonify({

            "success": False,

            "error":
                "Neteisinga platuma."

        }), 400


    if not -180 <= longitude <= 180:

        return jsonify({

            "success": False,

            "error":
                "Neteisinga ilguma."

        }), 400


    result = calculate_nearest_stations(

        latitude,

        longitude,

        bool(wind_only)

    )


    return jsonify(
        result
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "ok"

    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
