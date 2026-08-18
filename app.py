from flask import Flask, render_template, request, jsonify
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime, timedelta
from threading import Lock
import time


app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

STATIONS_API = "https://api.meteo.lt/v1/stations"

CACHE_DURATION = timedelta(minutes=15)

REQUEST_LIMIT = 60

REQUEST_WINDOW = 60

# Nominatim public API limit:
# maximum 1 request per second.
#
# We use 1.1 seconds to leave a small safety margin.

NOMINATIM_DELAY = 1.1


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
# STATION CACHE
# ============================================================

station_cache = {

    "stations": None,

    "timestamp": None

}


station_cache_lock = Lock()


# ============================================================
# GEOCODING CACHE
# ============================================================

geocode_cache = {}

geocode_cache_lock = Lock()


# ============================================================
# NOMINATIM
# ============================================================
#
# IMPORTANT:
# Create ONE geocoder for the application rather than creating
# a new one for every search.
#
# RateLimiter makes sure requests are separated by at least
# 1.1 seconds.
#

geolocator = Nominatim(

    user_agent=
        "ArtimiausiaMeteoStotis/1.0",

    timeout=15

)


rate_limited_geocode = RateLimiter(

    geolocator.geocode,

    min_delay_seconds=NOMINATIM_DELAY,

    max_retries=2,

    error_wait_seconds=5,

    swallow_exceptions=False

)


# ============================================================
# RATE LIMITING FOR OUR OWN WEBSITE
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
# LOAD METEO.LT STATIONS
# ============================================================

def load_stations():

    now = datetime.utcnow()


    # ========================================================
    # CHECK CACHE
    # ========================================================

    with station_cache_lock:

        if (

            station_cache["stations"] is not None

            and station_cache["timestamp"] is not None

            and now - station_cache["timestamp"]
            < CACHE_DURATION

        ):

            return station_cache["stations"]


    # ========================================================
    # GET METEO.LT STATIONS
    # ========================================================

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


        # ====================================================
        # ADD MANUAL STATIONS
        # ====================================================

        stations.extend(

            MANUAL_STATIONS

        )


        # ====================================================
        # SAVE CACHE
        # ====================================================

        with station_cache_lock:

            station_cache["stations"] = stations

            station_cache["timestamp"] = now


        return stations


    except Exception as error:

        print(

            f"Meteo.lt station error: {error}"

        )


        # ====================================================
        # USE PREVIOUS CACHE IF AVAILABLE
        # ====================================================

        with station_cache_lock:

            if station_cache["stations"] is not None:

                return station_cache["stations"]


        # ====================================================
        # FALLBACK
        # ====================================================

        return MANUAL_STATIONS.copy()


# ============================================================
# CALCULATE NEAREST STATIONS
# ============================================================

def calculate_nearest_stations(

    latitude,

    longitude,

    wind_only=False

):

    stations = load_stations()


    # ========================================================
    # WIND FILTER
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

            "success":
                False,

            "error":
                "Nerasta tinkamų meteorologijos stočių."

        }


    user_coordinates = (

        latitude,

        longitude

    )


    stations_with_distance = []


    # ========================================================
    # CALCULATE DISTANCES
    # ========================================================

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
    # THREE NEAREST
    # ========================================================

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


    # ========================================================
    # ALL WIND STATIONS FOR MAP
    # ========================================================

    if wind_only:

        map_stations = (

            stations_with_distance

        )

    else:

        map_stations = []


    return {

        "success":
            True,

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
# LOCATION SEARCH
# ============================================================

@app.route(

    "/api/location",

    methods=["POST"]

)
def location():

    if not check_rate_limit():

        return jsonify({

            "success":
                False,

            "error":
                "Per daug užklausų. "
                "Palaukite minutę."

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

            "success":
                False,

            "error":
                "Įveskite vietovę."

        }), 400


    # ========================================================
    # NORMALIZE CACHE KEY
    # ========================================================

    cache_key = (

        location_text

        .lower()

        .strip()

    )


    # ========================================================
    # CHECK CACHE
    # ========================================================

    with geocode_cache_lock:

        cached_result = (

            geocode_cache.get(

                cache_key

            )

        )


    if cached_result is not None:

        print(

            f"Geocoding cache hit: "
            f"{location_text}"

        )


        return jsonify(

            cached_result

        )


    # ========================================================
    # SEARCH QUERY
    # ========================================================

    search_query = location_text


    if (

        "lietuva"
        not in location_text.lower()

        and
        "lithuania"
        not in location_text.lower()

    ):

        search_query += ", Lithuania"


    # ========================================================
    # NOMINATIM REQUEST
    # ========================================================

    try:

        print(

            f"Geocoding: "
            f"{search_query}"

        )


        location_result = (

            rate_limited_geocode(

                search_query,

                exactly_one=True,

                addressdetails=True,

                language="lt",

                country_codes="lt"

            )

        )


        # ====================================================
        # NO RESULT
        # ====================================================

        if location_result is None:

            result = {

                "success":
                    False,

                "error":
                    f"Vietovė "
                    f"„{location_text}“ "
                    f"nerasta."

            }


            return jsonify(

                result

            ), 404


        # ====================================================
        # SUCCESS
        # ====================================================

        result = {

            "success":
                True,

            "name":
                location_result.address,

            "latitude":
                float(

                    location_result.latitude

                ),

            "longitude":
                float(

                    location_result.longitude

                )

        }


        # ====================================================
        # SAVE RESULT TO CACHE
        # ====================================================

        with geocode_cache_lock:

            geocode_cache[

                cache_key

            ] = result


        return jsonify(

            result

        )


    except Exception as error:

        print(

            f"Geocoding error: "
            f"{error}"

        )


        return jsonify({

            "success":
                False,

            "error":
                "Vietovės paieška šiuo metu "
                "laikinai nepasiekiama. "
                "Pabandykite dar kartą po kelių sekundžių."

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

            "success":
                False,

            "error":
                "Per daug užklausų. "
                "Palaukite minutę."

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


    # ========================================================
    # VALIDATE COORDINATES
    # ========================================================

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

            "success":
                False,

            "error":
                "Neteisingos koordinatės."

        }), 400


    if not -90 <= latitude <= 90:

        return jsonify({

            "success":
                False,

            "error":
                "Neteisinga platuma."

        }), 400


    if not -180 <= longitude <= 180:

        return jsonify({

            "success":
                False,

            "error":
                "Neteisinga ilguma."

        }), 400


    # ========================================================
    # FIND STATIONS
    # ========================================================

    result = (

        calculate_nearest_stations(

            latitude,

            longitude,

            bool(wind_only)

        )

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
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
