
# Cellar Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

Configuration:

Add to configuration.yaml:

```
cellar_tracker:
  username:  !secret cellar_tracker_username
  password:  !secret cellar_tracker_password
```


Sample Dashboard Config

```
title: Home
views:
    cards:
      - entities:
          - entity: sensor.cellar_tracker_total_bottles
          - entity: sensor.cellar_tracker_total_value
        show_icon: true
        type: glance
      - clickable: true
        columns:
          - data: sub_type
            name: Producer
          - data: count
            name: Count
            modify: parseFloat(x)
          - data: '%'
            modify: parseFloat(x).toFixed(0)
            name: Percentage
            suffix: '%'
          - data: value_avg
            name: Average Value
            prefix: $
            modify: parseFloat(x).toFixed(0)
        entities:
          include: sensor.cellar_tracker_producer*
        title: Bottles by Producer
        type: 'custom:flex-table-card'
        sort_by: count-
      - clickable: true
        columns:
          - data: sub_type
            name: Vintage
          - data: count
            name: Count
            modify: parseFloat(x)
          - data: '%'
            modify: parseFloat(x).toFixed(0)
            name: Percentage
            suffix: '%'
          - data: value_avg
            name: Average Value
            prefix: $
            modify: parseFloat(x).toFixed(0)
        entities:
          include: sensor.cellar_tracker_vintage*
        title: Bottles by Vintage
        type: 'custom:flex-table-card'
        sort_by: count-
      - clickable: true
        columns:
          - data: sub_type
            name: Country
          - data: count
            name: Count
            modify: parseFloat(x)
          - data: '%'
            modify: parseFloat(x).toFixed(0)
            name: Percentage
            suffix: '%'
          - data: value_avg
            name: Average Value
            prefix: $
            modify: parseFloat(x).toFixed(0)
        entities:
          include: sensor.cellar_tracker_country*
        title: Bottles by Country
        type: 'custom:flex-table-card'
        sort_by: count-
      - clickable: true
        columns:
          - data: sub_type
            name: Varietal
          - data: count
            name: Count
            modify: parseFloat(x)
          - data: '%'
            modify: parseFloat(x).toFixed(0)
            name: Percentage
            suffix: '%'
          - data: value_avg
            name: Average Value
            prefix: $
            modify: parseFloat(x).toFixed(0)
        entities:
          include: sensor.cellar_tracker_varietal*
        title: Bottles by Varietal
        type: 'custom:flex-table-card'
        sort_by: count-
    path: default_view
    title: Home
```