import math
import pandas as pd
import numpy as np
import textdistance
import time
import json
import mpu

from Server.Algo.ID3 import *

RESTAURANT = "restaurant"
STORE = "store"
BUS_STATION = "bus_station"
PLACE_KEYS = [RESTAURANT, STORE, BUS_STATION]


class DataParser:

    def __init__(self, config, progress_func):
        self.data_set_paths = config["data_set_paths"]
        self.global_fields = {field["type"]: field["name"] for field in config["global_fields"]}
        self.google_config = config["google_config"]
        self.cbs_config = config["cbs_config"]
        self.places_config = config["places_config"]
        self.rest_config = config["rest_config"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.google_df = None
        self.rest_data = {}
        self.cbs_data = {}
        self.places_data = {place_key: [] for place_key in PLACE_KEYS}
        self.common_words_strong = None
        self.common_words_weak = None
        self.data = {}

    def parse_data(self):
        self.get_raw_data()
        self.get_helper_data()
        self.prepare_data()
        self.fill_data()

    def fill_missing_data(self):
        self.fill_google_missing_data()
        self.fill_cbs_missing_data()

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')

    def get_raw_data(self):
        self.get_google_data()
        self.get_rest_data()
        self.get_cbs_data()
        self.get_places_data()

    def get_google_data(self):
        self.google_df = pd.read_json(self.data_set_paths["google"]).replace({np.nan: None})
        for field in self.google_config["fields"]:
            field_name = field["name"]
            field_type = field["type"]
            if field_type == "BOOL":
                self.google_df[field_name] = self.google_df[field_name].apply(self.parse_bool_field)
            elif field_type == "REVIEWS":
                self.google_df[field_name] = self.google_df[field_name].apply(self.parse_reviews_field)
            elif field_type == "GEO_LOCATION":
                self.google_df[field_name] = self.google_df[field_name].apply(self.parse_geo_location_field)

    def get_rest_data(self):
        rest_df = pd.read_json(self.data_set_paths["rest"])

        for row in range(len(rest_df)):
            city = rest_df[self.global_fields["CITY"]][row]
            if city not in self.rest_data:
                self.rest_data[city] = []
            self.rest_data[city].append(rest_df.iloc[row].to_dict())

    def get_cbs_data(self):
        cbs_df = pd.read_json(self.data_set_paths["cbs"]).replace({np.nan: None})

        for row in range(len(cbs_df)):
            key = (cbs_df[self.global_fields["STREET"]][row], cbs_df[self.global_fields["CITY"]][row])
            self.cbs_data[key] = {field["name"]: cbs_df[field["name"]][row] for field in self.cbs_config["fields"]}

    def get_places_data(self):
        google_places_df = pd.read_json(self.data_set_paths["google_places"])
        gov_df = pd.read_json(self.data_set_paths["gov"])

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

    def get_helper_data(self):
        common_words = self.get_common_words()
        self.common_words_strong = [key for key, value in common_words.items() if value >= 15]
        self.common_words_weak = [key for key, value in common_words.items() if value >= 5]

    def get_common_words(self):
        common_words = {}
        name_field = self.global_fields["NAME"]
        names = [value[name_field] for value in sum(self.rest_data.values(), [])] + self.google_df[name_field].tolist()
        for name in names:
            for word in set(name.split(" ")):
                if word not in common_words:
                    common_words[word.lower()] = 0
                common_words[word.lower()] += 1
        return common_words

    def prepare_data(self):
        fields = self.google_config["fields"] + self.cbs_config["fields"] + self.places_config["fields"] + self.rest_config["fields"]
        for field in fields:
            self.data[field["name"]] = []

    def fill_data(self):
        for row in range(len(self.google_df)):
            place_id = self.google_df[self.global_fields["PLACE_ID"]][row]
            name = self.google_df[self.global_fields["NAME"]][row]
            city = self.google_df[self.global_fields["CITY"]][row]
            street = self.google_df[self.global_fields["STREET"]][row]
            street_number = self.google_df[self.global_fields["STREET_NUMBER"]][row]
            geo_location = self.google_df[self.global_fields["GEO_LOCATION"]][row]
            address = (street or '') + " " + (street_number or '')
            self.progress_func(name, row + 1, len(self.google_df))
            self.fill_google_data(row)
            self.fill_cbs_data(city, street)
            self.fill_places_data(geo_location, place_id)
            self.fill_rest_data(name, address, city)

    def fill_google_data(self, row):
        self.add_data(self.google_config, self.google_df.iloc[row].to_dict())

    def fill_cbs_data(self, city, street):
        self.add_data(self.cbs_config, self.get_cbs_data_by_address(city, street))

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
            if cbs_key[1] == city and self.get_street_distance(cbs_key[0], street, reversed_street) > 0.9:
                return self.cbs_data.get(cbs_key)
        return None

    def get_street_distance(self, cbs_street, g_street, g_reversed_street):
        return max(self.text_distance(cbs_street, g_street), self.text_distance(cbs_street, g_reversed_street))

    def fill_places_data(self, geo_location, place_id):
        self.add_data(self.places_config, self.get_places_data_by_point(tuple(geo_location), place_id))

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
            point_distance = self.location_distance(point, tuple(value[self.global_fields["GEO_LOCATION"]]))
            for field in fields:
                distance_value = field["distance_value"] / 1000
                if point_distance <= distance_value:
                    res[field["name"]] += 1
        return res

    def fill_rest_data(self, name, address, city):
        name_field = self.global_fields["NAME"]
        address_field = self.global_fields["ADDRESS"]
        g_name_strong = self.get_filtered_name(name, self.common_words_strong)
        g_name_weak = self.get_filtered_name(name, self.common_words_weak)
        first_best = (0.9, None)
        second_best = (0.8, None)
        third_best = (0, None)
        for value in self.rest_data.get(city) or []:
            r_name_strong = self.get_filtered_name(value[name_field], self.common_words_strong)
            name_dist = self.text_distance(g_name_strong, r_name_strong)
            if name_dist > first_best[0]:
                first_best = (name_dist, value)

            if first_best[1] is None:
                place_dist = self.text_distance(value[address_field], address)
                if place_dist > 0.85 and name_dist > second_best[0]:
                    second_best = (name_dist, value)

            if first_best[1] is None and second_best[1] is None:
                r_name_weak = self.get_filtered_name(value[name_field], self.common_words_weak)
                common_words = self.get_common_words_size(g_name_weak, r_name_weak)
                if self.text_distance(g_name_weak, r_name_weak) > 0.8 and common_words > third_best[0]:
                    third_best = (common_words, value)

        self.add_data(self.rest_config, first_best[1] or second_best[1] or third_best[1])

    def add_data(self, config, data):
        for field in config["fields"]:
            field_name = field["name"]
            self.data[field_name].append(None if data is None else data[field_name])

    def fill_google_missing_data(self):
        df = pd.DataFrame(self.data)
        df = df.replace({np.nan: None})

        for field in self.google_config["fields"]:
            if "fill_by" in field:
                df.loc[df[field["name"]].isnull(), field["name"]] = self.predict_missing_data_by_field(df, field)
                self.data[field["name"]] = df[field["name"]].to_list()

    def fill_cbs_missing_data(self):
        for field in self.cbs_config["fields"]:
            self.fill_cbs_missing_data_by_col_name(field["name"])

    def fill_cbs_missing_data_by_col_name(self, col_name):
        blank_indexes = [idx for idx, val in enumerate(self.data[col_name]) if val is None]
        full_indexes = [idx for idx, val in enumerate(self.data[col_name]) if val is not None]
        for blank_idx in blank_indexes:
            values = [self.data[col_name][full_idx] for full_idx in full_indexes if self.is_places_close_by_indexes(blank_idx, full_idx)]
            if len(values) > 0:
                self.data[col_name][blank_idx] = round(np.mean(values), 3)

    def is_places_close_by_indexes(self, blank_idx, full_idx):
        blank_point = tuple(self.data[self.global_fields["GEO_LOCATION"]][blank_idx])
        full_point = tuple(self.data[self.global_fields["GEO_LOCATION"]][full_idx])
        return self.location_distance(blank_point, full_point) < 0.5

    @staticmethod
    def parse_bool_field(value):
        return None if value is None else bool(value)

    @staticmethod
    def parse_reviews_field(value):
        if value is None:
            return None
        reviews_words = set()
        for review in value:
            clean_r_text = review.replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\n', ' ').replace('?', ' ')
            reviews_words.update(clean_r_text.split(' '))
        return reviews_words

    @staticmethod
    def parse_geo_location_field(value):
        return None if value is None else [round(value["lat"], 7), round(value["lng"], 7)]

    @staticmethod
    def text_distance(s1, s2):
        if not s1 and not s2:
            return 0
        return textdistance.strcmp95.normalized_similarity(s1, s2)

    @staticmethod
    def location_distance(p1, p2):
        return mpu.haversine_distance(p1, p2)

    @staticmethod
    def get_filtered_name(name, filter_list):
        return " ".join([item for item in name.split(" ") if item not in filter_list])

    @staticmethod
    def get_common_words_size(name1, name2):
        return len(list(set(name1.lower().split(" ")) & set(name2.lower().split(" "))))

    @staticmethod
    def predict_missing_data_by_field(df, field):
        id3 = ID3([field["fill_by"]], max_depth=1, target_attribute=field["name"])
        train_set = df[df[field["name"]].notnull()].reset_index(drop=True)
        x_train = np.array(train_set[[field["fill_by"]]].copy())
        y_train = np.array(train_set[field["name"]].copy())
        id3.fit(x_train, y_train)
        test_set = df[df[field["name"]].isnull()].reset_index(drop=True)
        x_test = np.array(test_set[[field["fill_by"]]].copy())
        predict = id3.predict(x_test, True)
        predict_min = np.nanmin(np.array(predict, dtype=float))
        predict_max = np.nanmax(np.array(predict, dtype=float))
        if predict_min != predict_max:
            return np.array([None if p is None else (p == predict_max) for p in predict])
        else:
            values, counts = np.unique(y_train, return_counts=True)
            return np.array([values[np.argmax(counts)]] * len(x_test))


def parse_data(progress_func):
    try:
        with open('./Server/DataConfig/data-parser-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            parser = DataParser(config, progress_func)
            parser.parse_data()
            parser.fill_missing_data()
            parser.save_data()
    except IOError:
        print("Error")
