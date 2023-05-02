from Server.DataBuilder.CbsDataBuilder import *
import urllib.request
import json
import math


class GovDataBuilder:

    def __init__(self, config, progress_func):
        self.resource_id = config["resource_id"]
        self.base_url = config['base_url']
        self.api_url = config['api_url']
        self.city_codes = config['city_codes']
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.city_code_num_of_stations = {city_code: 0 for city_code in self.city_codes}
        self.num_of_stations = 0
        self.data = []

    def pre_build_data(self):
        for city_code in self.city_codes:
            stations_by_city_code = self.get_num_of_stations_by_city_code(city_code)
            self.city_code_num_of_stations[city_code] = stations_by_city_code
            self.num_of_stations += stations_by_city_code

    def build_data(self):
        for city_code in self.city_codes:
            self.get_raw_data_by_city(city_code)

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')

    def get_num_of_stations_by_city_code(self, city_code):
        url = self.api_url + '?resource_id=' + self.resource_id + '&q=' + str(city_code) + '&limit=0'
        raw_data = self.get_request_result(url)
        return raw_data["total"]

    def get_raw_data_by_city(self, city_code: int):
        url = self.api_url + '?resource_id=' + self.resource_id + '&q=' + str(city_code) + '&limit=100'
        next_url = self.get_raw_data_by_url(url)

        num_of_pages = math.floor(self.city_code_num_of_stations[city_code] / 100)
        for page in range(num_of_pages):
            next_url = self.get_raw_data_by_url(next_url)

    def get_raw_data_by_url(self, next_url: str):
        stations_data = self.get_request_result(next_url)
        for station in stations_data["records"]:
            self.data.append({
                "station_id": station["_id"],
                "geo_location": {
                    "lat": float(station["Lat"]),
                    "lng": float(station["Long"])
                }
            })
            if self.progress_func is not None:
                self.progress_func(f'{station["Neighborhood"]}, {station["CityName"]}', self.num_of_stations)
        return stations_data["_links"]["next"]

    def get_request_result(self, next_url: str):
        request = urllib.request.urlopen(self.base_url + next_url).read()
        return json.loads(request)["result"]


def gov_build_data():
    try:
        with open('./Server/DataConfig/gov-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            builder = GovDataBuilder(config, None)
            builder.pre_build_data()
            builder.build_data()
            builder.save_data()
    except IOError:
        print("Error")
