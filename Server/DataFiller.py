import pandas as pd
import numpy as np
from Server.Components.Time import Time

import textdistance

from Server.Algo.ID3 import *

RESTAURANT = "restaurant"
STORE = "store"
BUS_STATION = "bus_station"
PLACE_KEYS = [RESTAURANT, STORE, BUS_STATION]
cbs_data_path = "./DataOutput/cbs-data.csv"
cbs_data = pd.read_csv(cbs_data_path)
global_fields = [
        {
            "name": "place_id",
            "type": "PLACE_ID"
        },
        {
            "name": "city",
            "type": "CITY"
        },
        {
            "name": "street_number",
            "type": "STREET_NUMBER"
        },
        {
            "name": "street",
            "type": "STREET"
        },
        {
            "name": "geo_location",
            "type": "GEO_LOCATION"
        },
        {
            "name": "name",
            "type": "NAME"
        },
        {
            "name": "address",
            "type": "ADDRESS"
        }
    ]


def get_mean_activity_hour(activity_hours, is_open):
    idx = 0 if is_open else 1
    activity_hours_by_index = [activity_hours[day][idx] for day in range(5) if activity_hours[day] is not None]
    return None if len(activity_hours_by_index) == 0 else np.mean(activity_hours_by_index)


def is_open_on_saturday(activity_hours):
    if activity_hours[5] is None:
        return None
    latest_closing_time_friday = Time(hours=17, minutes=0)
    earliest_opening_time_saturday = Time(hours=19, minutes=0)
    open_on_friday = Time(total_minutes=activity_hours[5][1]).is_later_than(latest_closing_time_friday)
    open_on_saturday = Time(total_minutes=activity_hours[6][0]).is_earlier_than(earliest_opening_time_saturday) and activity_hours[6][0] != -1
    return open_on_friday or open_on_saturday

