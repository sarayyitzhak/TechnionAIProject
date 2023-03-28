from googleplaces import GooglePlaces, types, lang, ranking
from Server.DataBuilder.Utils import write_to_file
import time
import json


def get_raw_data(google_api_key: str, locations: list):
    data = []
    place_ids = set()
    for location in locations:
        data += get_raw_data_by_latitude(google_api_key, place_ids, location)
    return data


def get_raw_data_by_latitude(google_api_key: str, place_ids: set, location):
    delta = 1 / 110.574     # One kilometer
    lat = location["start_lat"]
    data = []
    while lat > location["end_lat"]:
        lat_lng = {"lat": lat, "lng": location["lng"]}
        data += get_raw_data_by_coordinates(google_api_key, place_ids, lat_lng)
        lat -= delta
    return data


def get_raw_data_by_coordinates(google_api_key: str, place_ids: set, lat_lng):
    data = []
    google_places = GooglePlaces(google_api_key)
    place_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE]
    for place_type in place_types:
        qr = google_places.nearby_search(language=lang.HEBREW, lat_lng=lat_lng, rankby=ranking.DISTANCE, types=[place_type])

        for place in qr.places:
            if place.place_id not in place_ids:
                if not place.rating:
                    continue
                place.get_details()
                data.append(place.details)
                place_ids.add(place.place_id)

        while qr.has_next_page_token:
            time.sleep(5)   # Waiting for the next page to be ready
            qr = google_places.nearby_search(language=lang.HEBREW, lat_lng=lat_lng, rankby=ranking.DISTANCE,
                                             types=place_types, pagetoken=qr.next_page_token)
            for place in qr.places:
                if place.place_id not in place_ids:
                    if not place.rating:
                        continue
                    place.get_details()
                    data.append(place.details)
                    place_ids.add(place.place_id)

    return data


def google_build_data():
    try:
        with open('./DataBuilder/google-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            write_to_file(get_raw_data(config["api_key"], config["locations"]), "./Dataset/google-data.json")
    except IOError:
        print("Error")
