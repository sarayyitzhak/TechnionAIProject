from Server.DataBuilder.CbsDataBuilder import *
import urllib.request
import json
import math


def get_bus_stations():
    data = []
    base_url = 'https://data.gov.il'
    city_codes = ['4000', '2500', '6800', '8200', '9600', '9500', '2100']
    for city in city_codes:
        url = base_url + '/api/3/action/datastore_search?resource_id=e873e6a2-66c1-494f-a677-f5e77348edb0&q=' + city
        request = urllib.request.urlopen(url).read()
        stations_data = json.loads(request)["result"]
        for station in stations_data["records"]:
            data.append(station)

        num_of_pages = math.floor(stations_data["total"] / 100)
        for page in range(num_of_pages):
            url = base_url + stations_data["_links"]["next"]
            request = urllib.request.urlopen(url).read()
            stations_data = json.loads(request)["result"]
            for station in stations_data["records"]:
                data.append(station)

    write_to_file(data, "./Dataset/bus-stations-data.json")

