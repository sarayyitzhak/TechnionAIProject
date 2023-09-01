import textdistance
from collections import Counter

from Server.Algo.ID3 import *
from Server.Components.Time import Time
from Server.utils import *

RESTAURANT = "restaurant"
STORE = "store"
BUS_STATION = "bus_station"
PLACE_KEYS = [RESTAURANT, STORE, BUS_STATION]


class DataFiller:

    def __init__(self, config):
        self.data_set_paths = config["data_set_paths"]
        self.global_fields = {field["type"]: field["name"] for field in config["global_fields"]}
        self.cbs_config = config["cbs_config"]
        self.places_config = config["places_config"]
        self.google_df = None
        self.cbs_data = {}
        self.places_data = {place_key: [] for place_key in PLACE_KEYS}

    def get_places_data(self):
        google_places_df = pd.read_csv(self.data_set_paths["google_places"])
        gov_df = pd.read_csv(self.data_set_paths["gov"])

        geo_location_field = self.global_fields["GEO_LOCATION"]
        google_places_df[geo_location_field] = google_places_df[geo_location_field].apply(self.parse_geo_location_field)
        gov_df[geo_location_field] = gov_df[geo_location_field].apply(self.parse_geo_location_field)

        for row in range(len(google_places_df)):
            if google_places_df["type"][row] == RESTAURANT:
                self.places_data[RESTAURANT].append(google_places_df.iloc[row, [0, 1]].to_dict())
            elif google_places_df["type"][row] == STORE:
                self.places_data[STORE].append(google_places_df.iloc[row, [1]].to_dict())

        for row in range(len(gov_df)):
            self.places_data[BUS_STATION].append(gov_df.iloc[row, [1]].to_dict())

    def get_places_data_by_point(self, point, place_id):
        data = {}
        for place_key in PLACE_KEYS:
            place_data = self.places_data[place_key]
            place_fields = [field for field in self.places_config["fields"] if field["type"].lower() == place_key]
            excluded_place_id = place_id if place_key == RESTAURANT else None
            data.update(self.get_near_by_places(place_data, place_fields, point, excluded_place_id))
        return data

    def get_near_by_places(self, data, fields, point, excluded_place_id):
        res = {field["name"]: 0 for field in fields}
        for value in data:
            if excluded_place_id is not None and value[self.global_fields["PLACE_ID"]] == excluded_place_id:
                continue
            point_distance = location_distance(point, tuple(value[self.global_fields["GEO_LOCATION"]]))
            for field in fields:
                distance_value = field["distance_value"] / 1000
                if point_distance <= distance_value:
                    res[field["name"]] += 1
        return res

    def get_cbs_data(self):
        cbs_df = pd.read_csv(self.data_set_paths["cbs"]).replace({np.nan: None})
        for row in range(len(cbs_df)):
            key = (cbs_df[self.global_fields["STREET"]][row], cbs_df[self.global_fields["CITY"]][row])
            self.cbs_data[key] = {field["name"]: cbs_df[field["name"]][row] for field in self.cbs_config["fields"]}

    def get_cbs_data_by_address(self, city, street):
        if city is None or street is None:
            return None
        reversed_street = " ".join(street.split(" ")[::-1])
        key = (street, city)
        reversed_key = (reversed_street, city)
        if key in self.cbs_data:
            return self.cbs_data.get(key)
        if reversed_key in self.cbs_data:
            return self.cbs_data.get(reversed_key)
        for cbs_key in self.cbs_data.keys():
            if cbs_key[1] == city and get_street_distance(cbs_key[0], street, reversed_street) > 0.9:
                return self.cbs_data.get(cbs_key)
        return None

    @staticmethod
    def parse_geo_location_field(value):
        if value is None:
            return None
        value = eval(value)
        return [round(value["lat"], 7), round(value["lng"], 7)]


class ActivityTimeFiller:

    @staticmethod
    def get_most_common_activity_hour(activity_hours, is_open):
        idx = 0 if is_open else 1
        activity_hours_by_index = Counter([activity_hours[day][idx] for day in range(7) if activity_hours[day] is not None])
        return None if len(activity_hours_by_index) == 0 else activity_hours_by_index.most_common()[0][0]

    @staticmethod
    def is_open_on_saturday(activity_hours):
        if activity_hours[5] is None or activity_hours[6] is None:
            return None
        latest_closing_time_friday = Time(hours=17, minutes=0)
        earliest_opening_time_saturday = Time(hours=19, minutes=0)
        open_on_friday = Time(total_minutes=activity_hours[5][1]).is_later_than(latest_closing_time_friday)
        open_on_saturday = Time(total_minutes=activity_hours[6][0]).is_earlier_than(earliest_opening_time_saturday) and \
                           activity_hours[6][0] != -1
        return open_on_friday or open_on_saturday
