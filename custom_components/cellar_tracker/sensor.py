"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from datetime import timedelta
import logging
import time
import pandas as pd
import re
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return

    devs = []

    master_data = hass.data[DOMAIN].get_readings()
    scan_interval = hass.data[DOMAIN].get_scan_interval()


    for sensor_type in master_data.keys():

        data = master_data[sensor_type]
        if(type(data) == dict):
            for key in data.keys():

                value = data[key]
                sensor_data = data.copy()
                sensor_data[sensor_type] = key

                devs.append(WineCellarSensor(sensor_type, key, sensor_data, scan_interval))
        else:
            devs.append(WineCellarSensor(sensor_type, None, data, scan_interval))

    add_entities(devs, True)


class WineCellarSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, sensor_type, sub_type, data, scan_interval):
        """Initialize the sensor."""

        self._sensor_type = sensor_type
        self._sub_type = sub_type
        self._data = data
        if(self._sub_type):
            self._slug = self._sub_type.lower()
            self._slug = re.sub(r'[^a-z0-9]+', '-', self._slug).strip('-')
            self._slug = re.sub(r'[_]+', '-', self._slug)
        else:
            self._slug = None
        # self.update()
        self.update = Throttle(scan_interval)(self._update)

    @property
    def name(self):
        """Return the name of the sensor."""
        if(self._sub_type):
            return "cellar_tracker." + self._sensor_type.lower() + "." + self._slug.lower()
        else:
            return "cellar_tracker." + self._sensor_type.lower()


    @property
    def extra_state_attributes(self):
        if(self._sub_type):
            return self._data

        return {}

    @property
    def icon(self):
        if(re.match(".+_value",self._sensor_type)):
            return "mdi:currency-usd"

        return "mdi:bottle-wine"

    @property
    def state(self):
        """Return the state of the sensor."""
        if(self._state == None):
            return 0

        if(re.match(".+_value",self._sensor_type)):
            return f"{self.hass.config.currency}{round(self._state,2)}"

        return self._state

    @property
    def unique_id(self):
        return "cellar_tracker." + self.name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if(re.match(".+_value",self._sensor_type)):
            return None

        return "bottles"

    def _update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug(f"Updating data for {self.name}")
        self.hass.data[DOMAIN].update()
        self._data = self.hass.data[DOMAIN].get_reading(self._sensor_type)

        if(self._sub_type):
            self._data = self._data[self._sub_type]
            self._state = self._data["count"]
        else:
            self._state = self._data
