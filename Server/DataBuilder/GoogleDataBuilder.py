from googleplaces import GooglePlaces, types, lang, ranking
from Server.DataBuilder.Utils import write_to_file
import time
import json


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
            if place.place_id not in self.place_ids:
                for common_type in list(set(self.place_types) & set(place.types)):
                    self.places.append({
                        "place_id": place.place_id,
                        "geo_location": place.geo_location,
                        "type": common_type
                    })
                self.place_ids.add(place.place_id)
            if place.place_id not in self.rest_ids:
                if len(list(set(self.rest_types) & set(place.types))) > 0 and place._rating != '':
                    place.get_details()
                    self.data.append(place.details)
                self.rest_ids.add(place.place_id)


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
