from cellartracker import cellartracker
import pandas as pd
import numpy as np
import logging

from random import seed
from random import randint
from datetime import timedelta

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle




"""Example Load Platform integration."""
DOMAIN = 'cellar_tracker'

SCAN_INTERVAL = timedelta(seconds=3600)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=3600)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
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
    

    
    hass.data[DOMAIN] = WineCellarData(username, password)
    hass.data[DOMAIN].update()


    
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    

    return True

class WineCellarData:
    """Get the latest data and update the states."""

    def __init__(self, username, password):
        """Init the Canary data object."""

        # self._api = Api(username, password, timeout)

        # self._locations_by_id = {}
        # self._readings_by_device_id = {}
        self._username = username
        self._password = password
        

    def get_reading(self, key):
      return self._data[key]

    def get_readings(self):
      return self._data

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self, **kwargs):
      data = {}
      username = self._username
      password = self._password


      client = cellartracker.CellarTracker(username, password)
      list = client.get_inventory()
      df = pd.DataFrame(list)
      df[["Price","Valuation"]] = df[["Price","Valuation"]].apply(pd.to_numeric)

      groups = ['Varietal', 'Country', 'Vintage', 'Producer', 'Type', 'Location', 'Bin']

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
      

    
