"""Constants for Google Travel Time."""
DOMAIN = "google_public_transport_departures"

ATTRIBUTION = "Powered by Google"

CONF_DESTINATION = "destination"
CONF_OPTIONS = "options"
CONF_ORIGIN = "origin"
CONF_TRAVEL_MODE = "travel_mode"
CONF_LANGUAGE = "language"
CONF_AVOID = "avoid"
CONF_UNITS = "units"
CONF_ARRIVAL_TIME = "arrival_time"
CONF_DEPARTURE_TIME = "departure_time"
CONF_TRAFFIC_MODEL = "traffic_model"
CONF_TRANSIT_MODE = "transit_mode"
CONF_TRANSIT_ROUTING_PREFERENCE = "transit_routing_preference"
CONF_TIME_TYPE = "time_type"
CONF_TIME = "time"

ARRIVAL_TIME = "Arrival Time"
DEPARTURE_TIME = "Departure Time"
TIME_TYPES = [ARRIVAL_TIME, DEPARTURE_TIME]

DEFAULT_NAME = "Google Travel Time"

ALL_LANGUAGES = [
    "en",
]

AVOID = ["tolls", "highways", "ferries", "indoor"]
TRANSIT_PREFS = ["less_walking", "fewer_transfers"]
TRANSPORT_TYPE = ["bus", "subway", "train", "tram", "rail"]
TRAVEL_MODE = ["driving", "walking", "bicycling", "transit"]
TRAVEL_MODEL = ["best_guess", "pessimistic", "optimistic"]

# googlemaps library uses "metric" or "imperial" terminology in distance_matrix
UNITS_METRIC = "metric"
UNITS_IMPERIAL = "imperial"
UNITS = [UNITS_METRIC, UNITS_IMPERIAL]
