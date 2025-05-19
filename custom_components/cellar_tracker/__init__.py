from cellartracker import cellartracker
import pandas as pd
import numpy as np
import logging

from random import seed
from random import randint
from datetime import timedelta

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_SCAN_INTERVAL
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers import discovery as hdisco

"""Example Load Platform integration."""
DOMAIN = 'cellar_tracker'

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=3600): int
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
   """Your controller/hub specific code."""
   # Data that you want to share with your platforms

   conf = config[DOMAIN]

   username = conf[CONF_USERNAME]
   password = conf[CONF_PASSWORD]
   # Enforce a low limit of 30
   scan_interval_seconds = conf[CONF_SCAN_INTERVAL]
   if scan_interval_seconds < 30:
     _LOGGER.debug("Overriding scan interval to 30 due to low value of {scan_interval_seconds}")
     scan_interval_seconds = 30
   else:
     _LOGGER.debug(f"Using configured scan_interval of {scan_interval_seconds}")
   scan_interval = timedelta(seconds=scan_interval_seconds)

   hass.data[DOMAIN] = WineCellarData(username, password, scan_interval)
   hass.data[DOMAIN].update()

   hdisco.load_platform(hass, 'sensor', DOMAIN, {}, config)

   return True

class WineCellarData:
    """Get the latest data and update the states."""

    def __init__(self, username, password, scan_interval):
        """Init the Canary data object."""

        self._username = username
        self._password = password
        _LOGGER.debug(f"Initiating with scan interval of {scan_interval}")
        self.update = Throttle(scan_interval)(self._update)
        self._scan_interval = scan_interval

    def get_reading(self, key):
      return self._data[key]

    def get_readings(self):
      return self._data

    def get_scan_interval(self):
      return self._scan_interval

    def _update(self, **kwargs):
      _LOGGER.debug("Updating cellar tracker data")
      data = {}
      username = self._username
      password = self._password

      client = cellartracker.CellarTracker(username, password)
      inventory = client.get_inventory()
      df = pd.DataFrame(inventory)
      df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric)

      groups = ['Varietal', 'Country', 'Vintage', 'Producer', 'Type', 'Location', 'Appellation', 'StoreName']

      for group in groups:
        group_data = df.groupby(group).agg({'iWine':'count','Valuation':['sum','mean']})
        group_data.columns = group_data.columns.droplevel(0)
        group_data["%"] = 1
        group_data["%"] = (group_data['count']/group_data['count'].sum() ) * 100
        group_data.columns = ["count", "value_total", "value_avg", "%"]
        data[group] = {}
        for row, item in group_data.iterrows():
          if row == "1001":
            row = "NV"
          data[group][row] = item.to_dict()
          data[group][row]["sub_type"] = row

      data["total_bottles"] = len(df)
      data["total_value"] = df['Valuation'].sum()
      data["average_value"] = df['Valuation'].mean()
      self._data = data
