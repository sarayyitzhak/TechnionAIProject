from googleplaces import GooglePlaces, types, lang, ranking

from Server.Components.Time import Time
from Server.DataFiller import *
from Server.DataBuilder.Utils import write_to_file
import time
import json
import math
import pandas as pd
import numpy as np


class GoogleDataBuilder:

    def __init__(self, config, progress_func):
        self.debug_mode = config["DEBUG"]
        self.full_data_path = config["DEBUG_full_data_path"]
        self.google_places = GooglePlaces(config["api_key"])
        self.locations = config["locations"]
        self.estimated_restaurants_total = config["estimated_restaurants_total"]
        self.output_path = config["output_path"]
        self.output_places_path = config["output_places_path"]
        self.progress_func = progress_func
        self.data = []
        self.places = []
        self.place_ids = set()
        self.rest_ids = set()
        self.lat_delta = 1 / 110.574  # One kilometer
        self.place_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE, types.TYPE_STORE]
        self.rest_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE]

    def build_data(self):
        if self.debug_mode:
            self.build_data_debug()
        else:
            for location in self.locations:
                self.get_raw_data_by_latitude(location)

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')
        if not self.debug_mode:
            pd.DataFrame(self.places).to_csv(self.output_places_path, index=False, encoding='utf-8-sig')

    def build_data_debug(self):
        with open(self.full_data_path, 'r', encoding='utf-8') as f:
            for details in json.load(f):
                if "rating" in details:
                    self.add_place_details(details)
                    time.sleep(0.01)    # Illustrate waiting

    def get_raw_data_by_latitude(self, location):
        lat = location["start_lat"]
        while lat > location["end_lat"]:
            lat_lng = {"lat": lat, "lng": location["lng"]}
            self.get_raw_data_by_coordinates(lat_lng)
            lat -= self.lat_delta

    def get_raw_data_by_coordinates(self, lat_lng):
        for place_type in self.place_types:
            qr = self.create_query(lat_lng, place_type, None)
            self.get_raw_data_by_query(qr)

            while qr.has_next_page_token:
                time.sleep(5)   # Waiting for the next page to be ready
                qr = self.create_query(lat_lng, place_type, qr.next_page_token)
                self.get_raw_data_by_query(qr)

    def create_query(self, lat_lng, place_type, next_page_token):
        return self.google_places.nearby_search(language=lang.HEBREW, lat_lng=lat_lng, rankby=ranking.DISTANCE,
                                                types=[place_type], pagetoken=next_page_token)

    def get_raw_data_by_query(self, qr):
        for place in qr.places:
            is_rest = len(list(set(self.rest_types) & set(place.types))) > 0
            if place.place_id not in self.place_ids:
                self.places.append({
                    "place_id": place.place_id,
                    "geo_location": place.geo_location,
                    "type": types.TYPE_RESTAURANT if is_rest else types.TYPE_STORE
                })
                self.place_ids.add(place.place_id)
            if place.place_id not in self.rest_ids:
                if is_rest and place["_rating"] != '':
                    place.get_details()
                    self.add_place_details(place.details)
                self.rest_ids.add(place.place_id)

    def add_place_details(self, place_details):
        details = self.get_data_details(place_details)
        self.data.append(details)
        if self.progress_func is not None:
            self.progress_func(details['name'], self.estimated_restaurants_total)

    def get_data_details(self, details):
        data = {}
        bool_keys = ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch',
                   'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout',
                   'wheelchair_accessible_entrance', 'curbside_pickup']
        str_keys = ['place_id', 'name']
        num_keys = ['rating', 'price_level', 'user_ratings_total']
        not_none_keys = ['website']
        for key in bool_keys:
            data[key] = self.get_bool_value(details, key)
        for key in str_keys:
            data[key] = self.get_str_value(details, key)
        for key in num_keys:
            data[key] = self.get_num_value(details, key)
        for key in not_none_keys:
            data[key] = self.get_not_none_value(details, key)

        data.update(self.get_address(details))

        activity_hours = self.get_activity_hours(details)
        data['sunday_activity_hours'] = activity_hours[0]
        data['monday_activity_hours'] = activity_hours[1]
        data['tuesday_activity_hours'] = activity_hours[2]
        data['wednesday_activity_hours'] = activity_hours[3]
        data['thursday_activity_hours'] = activity_hours[4]
        data['friday_activity_hours'] = activity_hours[5]
        data['saturday_activity_hours'] = activity_hours[6]

        data["open_activity_hour"] = ActivityTimeFiller.get_most_common_activity_hour(activity_hours, True)
        data["close_activity_hour"] = ActivityTimeFiller.get_most_common_activity_hour(activity_hours, False)

        data["open_on_saturday"] = ActivityTimeFiller.is_open_on_saturday(activity_hours)

        return data

    @staticmethod
    def get_bool_value(details, key):
        return None if key not in details or math.isnan(details[key]) else bool(details[key])

    @staticmethod
    def get_str_value(details, key):
        return None if key not in details or type(details[key]) is not str else details[key]

    @staticmethod
    def get_num_value(details, key):
        return None if key not in details or math.isnan(details[key]) else details[key]

    @staticmethod
    def get_not_none_value(details, key):
        return key in details and type(details[key]) is str

    @staticmethod
    def get_address(details):
        address = {
            "city": None,
            "street": None,
            "street_number": None,
            "full_address": details["vicinity"],
            "geo_location": details["geometry"]["location"]
        }
        for component in details["address_components"]:
            if "locality" in component["types"]:
                address["city"] = component["long_name"]
            if "route" in component["types"]:
                address["street"] = component["long_name"]
            if "street_number" in component["types"]:
                address["street_number"] = component["long_name"]
        return address

    @staticmethod
    def get_activity_hours(details):
        activity_hours = {key: None for key in range(7)}
        if "opening_hours" in details and type(details["opening_hours"]) is dict:
            periods = details["opening_hours"]["periods"]
            if "close" not in periods[0]:
                for day in range(7):
                    activity_hours[day] = [0, 2 * Time.ONE_DAY]
            else:
                for period in periods:
                    day = period["open"]["day"]
                    open_total_minutes = Time(period["open"]["time"]).get_total_minutes()
                    close_total_minutes = Time(period["close"]["time"]).get_total_minutes()
                    close_total_minutes += 0 if open_total_minutes < close_total_minutes else Time.ONE_DAY
                    current_activity_hours = [math.inf, -math.inf] if activity_hours[day] is None else activity_hours[day]
                    open_hours = min(open_total_minutes, current_activity_hours[0])
                    close_hours = max(close_total_minutes, current_activity_hours[1])
                    activity_hours[day] = [open_hours, close_hours]
                for day in range(7):
                    if activity_hours[day] is None:
                        activity_hours[day] = [-1, -1]

        return activity_hours
