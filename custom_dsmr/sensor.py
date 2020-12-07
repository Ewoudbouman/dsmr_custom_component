"""Sensor for the custom dsmr api logger."""
import asyncio
import logging
from datetime import timedelta

import async_timeout
from aiohttp import ClientError

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import (
    API_V1_ACTUAL,
    API_V1_HIST_DAYS,
    API_V1_HIST_HOURS,
    API_V1_HIST_MONTHS,
    DOMAIN,
    SENSOR_FORMAT,
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_LIVE_UPDATES = timedelta(seconds=60)
MIN_TIME_BETWEEN_LONG_UPDATES = timedelta(hours=1)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the DSMR sensors."""
    session = async_get_clientsession(hass)
    config = hass.data[DOMAIN][config_entry.entry_id]
    host_api_actual = config["host"] + API_V1_ACTUAL
    host_api_hist_hours = config["host"] + API_V1_HIST_HOURS
    host_api_hist_days = config["host"] + API_V1_HIST_DAYS
    host_api_hist_months = config["host"] + API_V1_HIST_MONTHS

    sensor_entities = []

    # The DSMR logger exposes multiple restAPI's for the data we collect.
    # The current and historical measurements are requested at different
    # intervals to limit the total number of requests.
    #
    # Creation of the current measurement sensors.
    # Add the sensors exposed by the dsmr client.
    live_data = DSMRLiveData(session, host_api_actual)
    for key in SENSOR_FORMAT:
        if SENSOR_FORMAT[key].get("period") == "actual":
            sensor_entities.append(DSMRSensor(key, live_data))

    # Creation of the optional historical sensors.
    if config["history_hour"]:
        hist_data = DSMRHistData(session, host_api_hist_hours, "hours")
        for key in SENSOR_FORMAT:
            if SENSOR_FORMAT[key].get("period") == "hours":
                sensor_entities.append(DSMRSensor(key, hist_data))

    if config["history_day"]:
        hist_data = DSMRHistData(session, host_api_hist_days, "days")
        for key in SENSOR_FORMAT:
            if SENSOR_FORMAT[key].get("period") == "days":
                sensor_entities.append(DSMRSensor(key, hist_data))

    if config["history_month"]:
        hist_data = DSMRHistData(session, host_api_hist_months, "months")
        for key in SENSOR_FORMAT:
            if SENSOR_FORMAT[key].get("period") == "months":
                sensor_entities.append(DSMRSensor(key, hist_data))

    async_add_devices(sensor_entities, True)


class DSMRLiveData:
    """Representation of a DSMR sensor with live usage data."""

    def __init__(self, session, host_api_actual):
        """Initialize the live data object."""
        self._data = None
        self._session = session
        self._api = host_api_actual

    @property
    def data(self):
        """Return the data."""
        return self._data

    @property
    def api(self):
        """Return the api."""
        return self._api

    def latest_data(self, sensor):
        """Return the latest available data."""
        if self._data is None:
            return None
        return self._data.get(sensor).get("value", 0)

    def parse_live_data(self, json_data):
        """Extract the live measurements from the DSMR response."""
        # The json_data contains all values for the actual power and
        # energy and gas (running total) meter readings.
        #
        # All values are stored in a dictionary using the meter reading
        # as the key.
        # E.G.: data["energy_delivered_tariff1"] = 1500
        if json_data is not None:
            formatted = {}
            try:
                for received in json_data["actual"]:
                    formatted[received.pop("name")] = received
                self._data = formatted
            except KeyError as err:
                _LOGGER.debug("Failed to read the JSON message using key %s", err)
                self._data = None

    @Throttle(MIN_TIME_BETWEEN_LIVE_UPDATES)
    async def async_update(self):
        """Request the live measurements from the DSMR logger."""
        try:
            with async_timeout.timeout(10):
                response = await self._session.get(self.api)
                json_data = await response.json()
        except (asyncio.TimeoutError):
            _LOGGER.error("Timeout connecting to the DSMR meter")
            self._data = None
        except (ClientError) as err:
            _LOGGER.error("Error retrieving DSMR data: %s", repr(err))
            self._data = None

        return self.parse_live_data(json_data)


class DSMRHistData:
    """Manages the data retreived from the DSMR end device."""

    def __init__(self, session, host_api, period):
        """Initialize the data object."""
        self._data = None
        self._session = session
        self._api = host_api
        self._period = period

    @property
    def data(self):
        """Return the data."""
        return self._data

    @property
    def api(self):
        """Return the api."""
        return self._api

    def latest_data(self, sensor):
        """Return the latest historical data."""
        if self._data is None:
            return None
        return self._data.get(sensor)

    def parse_historical_data(self, json_data):
        """Extract the historical statistics from the DSMR response."""
        # The historical data contains the delivered energy, delivered gas and
        # returned energy values for the requested time period.
        # All values are represented by a peak and offpeak value.
        #
        # All values are stored as a running total of all previous periods.
        # We take the current value subtracted by the previous value to
        # get the current energy or gass usage.
        if json_data is not None:
            formatted = {}
            try:
                for i in range(2):
                    cur_del = (
                        json_data[self._period][i]["edt1"]
                        + json_data[self._period][i]["edt2"]
                    )
                    prev_del = (
                        json_data[self._period][i + 1]["edt1"]
                        + json_data[self._period][i + 1]["edt2"]
                    )
                    formatted[("energy_" + self._period + "_delivered_" + str(i))] = (
                        cur_del - prev_del
                    )
                    cur_ret = (
                        json_data[self._period][i]["ert1"]
                        + json_data[self._period][i]["ert2"]
                    )
                    prev_ret = (
                        json_data[self._period][i + 1]["ert1"]
                        + json_data[self._period][i + 1]["ert2"]
                    )
                    formatted[("energy_" + self._period + "_returned_" + str(i))] = (
                        cur_ret - prev_ret
                    )
                    cur_gas = json_data[self._period][i]["gdt"]
                    prev_gas = json_data[self._period][i + 1]["gdt"]
                    formatted[("gas_" + self._period + "_delivered_" + str(i))] = (
                        cur_gas - prev_gas
                    )
                self._data = formatted
            except KeyError as err:
                _LOGGER.debug("Failed to read the JSON message using key %s", err)
                self._data = None

    @Throttle(MIN_TIME_BETWEEN_LONG_UPDATES)
    async def async_update(self):
        """Request the historical statistics from the DSMR logger."""
        try:
            with async_timeout.timeout(10):
                response = await self._session.get(self.api)
                json_data = await response.json()
        except (asyncio.TimeoutError):
            _LOGGER.error("Timeout connecting to the DSMR meter")
            self._data = None
        except (ClientError) as err:
            _LOGGER.error("Error retrieving DSMR data: %s", repr(err))
            self._data = None

        return self.parse_historical_data(json_data)


class DSMRSensor(Entity):
    """Manages the individual sensors representing the measurements of the DSMR device."""

    def __init__(self, sensor, data):
        """Initialize the sensor."""
        self._sensor = sensor
        self._data = data
        self._name = SENSOR_FORMAT[sensor].get("name")
        self._icon = SENSOR_FORMAT[sensor].get("icon")
        self._unit_of_measurement = SENSOR_FORMAT[sensor].get("unit")
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the sensor icon for the frontend ."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return self._unit_of_measurement

    async def async_update(self):
        """Update the sensor with the latest received data."""
        await self._data.async_update()
        new_data = self._data.latest_data(self._sensor)
        if new_data is not None:
            self._state = new_data
            _LOGGER.debug(
                "Updated sensor %s: new state =  %s", self._sensor, self._state
            )