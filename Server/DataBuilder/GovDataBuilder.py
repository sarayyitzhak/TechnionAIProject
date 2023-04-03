from Server.DataBuilder.CbsDataBuilder import *
import urllib.request
import json
import math

# "place_id": "ChIJNwkAq1i6HRURQ5cbulHEMR8",
# "geo_location": {
#     "lat": 32.7934217,
#     "lng": 35.01110729999999
# },
# "type": "store"


class GovDataBuilder:

    def __init__(self, resource_id: str, base_url: str, api_url: str, city_codes: list):
        self.resource_id = resource_id
        self.base_url = base_url
        self.api_url = api_url
        self.city_codes = city_codes
        self.data = []

    def build_data(self):
        for city_code in self.city_codes:
            self.get_raw_data_by_city(city_code)

    def get_raw_data_by_city(self, city_code: int):
        url = self.api_url + '?resource_id=' + self.resource_id + '&q=' + str(city_code)
        total, next_url = self.get_raw_data_by_url(url)

        num_of_pages = math.floor(total / 100)
        for page in range(num_of_pages):
            _, next_url = self.get_raw_data_by_url(next_url)

    def get_raw_data_by_url(self, next_url: str):
        request = urllib.request.urlopen(self.base_url + next_url).read()
        stations_data = json.loads(request)["result"]
        for station in stations_data["records"]:
            self.data.append({
                "station_id": station["_id"],
                "geo_location": {
                    "lat": float(station["Lat"]),
                    "lng": float(station["Long"])
                }
            })
        return stations_data["total"], stations_data["_links"]["next"]


def gov_build_data():
    try:
        with open('./DataConfig/gov-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            builder = GovDataBuilder(config["resource_id"], config['base_url'], config['api_url'], config['city_codes'])
            builder.build_data()
            write_to_file(builder.data, config["output_path"])
    except IOError:
        print("Error")
