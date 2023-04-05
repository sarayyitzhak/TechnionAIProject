from googleplaces import GooglePlaces, types, lang, ranking

from Server.Components.Time import Time
from Server.DataBuilder.Utils import write_to_file
import time
import json
import math


class GoogleDataBuilder:

    def __init__(self, google_api_key: str, locations: list):
        self.google_places = GooglePlaces(google_api_key)
        self.locations = locations
        self.data = []
        self.places = []
        self.place_ids = set()
        self.rest_ids = set()
        self.lat_delta = 1 / 110.574  # One kilometer
        self.place_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE, types.TYPE_STORE]
        self.rest_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE]

    def build_data(self):
        for location in self.locations:
            self.get_raw_data_by_latitude(location)

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
                time.sleep(5)  # Waiting for the next page to be ready
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
                    self.data.append(self.get_data_details(place.details))
                self.rest_ids.add(place.place_id)

    def get_data_details(self, details):
        data = {}
        bool_keys = ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch',
                   'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout',
                   'wheelchair_accessible_entrance', 'curbside_pickup']
        str_keys = ['place_id', 'website', 'name']
        num_keys = ['rating', 'price_level', 'user_ratings_total']
        for key in bool_keys:
            data[key] = None if math.isnan(details[key]) else bool(details[key])
        for key in str_keys:
            data[key] = None if type(details[key]) is not str else details[key]
        for key in num_keys:
            data[key] = None if math.isnan(details[key]) else details[key]

        data["address"] = self.get_address(details)

        activity_hours = self.get_activity_hours(details)
        data['sunday_activity_hours'] = activity_hours[0]
        data['monday_activity_hours'] = activity_hours[1]
        data['tuesday_activity_hours'] = activity_hours[2]
        data['wednesday_activity_hours'] = activity_hours[3]
        data['thursday_activity_hours'] = activity_hours[4]
        data['friday_activity_hours'] = activity_hours[5]
        data['saturday_activity_hours'] = activity_hours[6]

        data["reviews"] = self.get_reviews(details)

        return data

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
        activity_hours = {key: [] for key in range(7)}
        if type(details["opening_hours"]) is dict:
            periods = details["opening_hours"]["periods"]
            if "close" not in periods[0]:
                for day in range(7):
                    activity_hours[day].append({'open': -1, 'close': -1})
            else:
                for period in periods:
                    day = period["open"]["day"]
                    open_total_minutes = Time(period["open"]["time"]).get_total_minutes()
                    close_total_minutes = Time(period["close"]["time"]).get_total_minutes()
                    close_total_minutes += 0 if open_total_minutes < close_total_minutes else Time.ONE_DAY
                    activity_hours[day].append({"open": open_total_minutes, "close": close_total_minutes})
        return activity_hours

    @staticmethod
    def get_reviews(details):
        return None if type(details["reviews"]) is not list else [review["text"] for review in details["reviews"]]


def google_build_data():
    try:
        with open('./DataConfig/google-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            builder = GoogleDataBuilder(config["api_key"], config["locations"])
            builder.build_data()
            write_to_file(builder.data, config["output_path"])
            write_to_file(builder.places, config["output_places_path"])
    except IOError:
        print("Error")
