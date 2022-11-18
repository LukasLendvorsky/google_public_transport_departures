"""Support for Google travel time sensors."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

from googlemaps import Client
from googlemaps.directions import directions

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STARTED,
    TIME_MINUTES,
)
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.location import find_coordinates
import homeassistant.util.dt as dt_util

from .const import (
    ATTRIBUTION,
    CONF_ARRIVAL_TIME,
    CONF_DEPARTURE_TIME,
    CONF_DESTINATION,
    CONF_ORIGIN,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


def convert_time_to_utc(timestr):
    """Take a string like 08:00:00 and convert it to a unix timestamp."""
    combined = datetime.combine(
        dt_util.start_of_local_day(), dt_util.parse_time(timestr)
    )
    if combined < datetime.now():
        combined = combined + timedelta(days=1)
    return dt_util.as_timestamp(combined)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Google travel time sensor entry."""
    api_key = config_entry.data[CONF_API_KEY]
    origin = config_entry.data[CONF_ORIGIN]
    destination = config_entry.data[CONF_DESTINATION]
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)

    client = Client(api_key, timeout=10)

    sensor = GoogleTravelTimeSensor(
        config_entry, name, api_key, origin, destination, client
    )

    async_add_entities([sensor], False)


class GoogleTravelTimeSensor(SensorEntity):
    """Representation of a Google travel time sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, config_entry, name, api_key, origin, destination, client):
        """Initialize the sensor."""
        self._name = name
        self._config_entry = config_entry
        self._unit_of_measurement = TIME_MINUTES
        self._matrix = None
        self._api_key = api_key
        self._unique_id = config_entry.entry_id
        self._client = client
        self._origin = origin
        self._destination = destination
        self._resolved_origin = None
        self._resolved_destination = None

    async def async_added_to_hass(self) -> None:
        """Handle when entity is added."""
        if self.hass.state != CoreState.running:
            self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self.first_update
            )
        else:
            await self.first_update()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._matrix is None:
            return None

        _data = datetime.fromtimestamp(self._matrix[0]["timestamp"])
        return _data

    @property
    def device_info(self) -> DeviceInfo:
        """Return device specific attributes."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._api_key)},
            name=DOMAIN,
        )

    @property
    def unique_id(self) -> str:
        """Return unique ID of entity."""
        return self._unique_id

    @property
    def name(self):
        """Get the name of the sensor."""
        return self._name

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self._matrix is None:
            return None

        res = {}
        id = 0
        for row in self._matrix:
            res["departure_" + str(id)] = row["departure_time"]
            res["line_" + str(id)] = row["line"]
            id += 1

        return res

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    async def first_update(self, _=None):
        """Run the first update and write the state."""
        await self.hass.async_add_executor_job(self.update)
        self.async_write_ha_state()

    def update(self) -> None:
        """Get the latest data from Google."""
        now = datetime.now()

        _LOGGER.debug(
            "Getting update for origin: %s destination: %s",
            self._origin,
            self._destination,
        )

        directions_result = directions(
            self._client,
            self._origin,
            self._destination,
            mode="transit",
            departure_time=now,
            alternatives=True,
        )

        result = []
        for route in directions_result:
            transit = route["legs"][0]["steps"][1]["transit_details"]
            result.append(
                {
                    "line": transit["line"]["short_name"],
                    "departure_time": datetime.fromtimestamp(
                        transit["departure_time"]["value"]
                    ).strftime("%H:%M"),
                    "timestamp": transit["departure_time"]["value"],
                }
            )

        result.sort(key=lambda row: row["timestamp"])

        self._matrix = result
