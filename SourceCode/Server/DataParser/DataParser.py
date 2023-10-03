from SourceCode.Server.DataParser.DataFiller import *
from SourceCode.Server.Utils.Utils import *

RESTAURANT = "restaurant"
STORE = "store"
BUS_STATION = "bus_station"
PLACE_KEYS = [RESTAURANT, STORE, BUS_STATION]


class DataParser:

    def __init__(self, config, progress_func):
        self.data_set_paths = config["data_set_paths"]
        self.target_field = config["target_field"]
        self.global_fields = {field["type"]: field["name"] for field in config["global_fields"]}
        self.fields_to_remove = config["fields_to_remove"]
        self.google_config = config["google_config"]
        self.cbs_config = config["cbs_config"]
        self.places_config = config["places_config"]
        self.rest_config = config["rest_config"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.google_df = None
        self.rest_data = {}
        self.common_words = None
        self.data = {}
        self.data_filler = DataFiller(config)

    def pre_parse_data(self):
        self.get_raw_data()
        self.get_helper_data()
        self.prepare_data()

    def parse_data(self):
        for row in range(len(self.google_df)):
            self.fill_data(row)

    def fill_missing_data(self):
        self.fill_google_missing_data()
        self.fill_cbs_missing_data()
        self.fill_rest_missing_data()

    def clean_data(self):
        for field_name in self.fields_to_remove:
            del self.data[field_name]

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')

    def get_raw_data(self):
        self.get_google_data()
        self.get_rest_data()
        self.data_filler.get_cbs_data()
        self.data_filler.get_places_data()

    def get_google_data(self):
        self.google_df = pd.read_csv(self.data_set_paths["google"]).replace({np.nan: None})
        for field in self.google_config["fields"]:
            field_name = field["name"]
            field_type = field["type"]
            if field_type == "BOOL":
                self.google_df[field_name] = self.google_df[field_name].apply(self.parse_bool_field)
            elif field_type == "GEO_LOCATION":
                self.google_df[field_name] = self.google_df[field_name].apply(self.data_filler.parse_geo_location_field)

    def get_rest_data(self):
        rest_df = pd.read_csv(self.data_set_paths["rest"])

        for row in range(len(rest_df)):
            city = rest_df[self.global_fields["CITY"]][row]
            if city not in self.rest_data:
                self.rest_data[city] = []
            self.rest_data[city].append(rest_df.iloc[row].to_dict())

    def get_helper_data(self):
        self.get_common_words_data()

    def get_common_words_data(self):
        self.common_words = [key for key, value in self.get_common_words().items() if value >= 15]

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
        fields = []
        fields += self.google_config["fields"]
        fields += self.cbs_config["fields"]
        fields += self.places_config["fields"]
        fields += self.rest_config["fields"]
        fields.append(self.target_field)
        for field in fields:
            self.data[field["name"]] = []

    def fill_data(self, row):
        place_id = self.google_df[self.global_fields["PLACE_ID"]][row]
        name = self.google_df[self.global_fields["NAME"]][row]
        city = self.google_df[self.global_fields["CITY"]][row]
        street = self.google_df[self.global_fields["STREET"]][row]
        street_number = self.google_df[self.global_fields["STREET_NUMBER"]][row]
        geo_location = self.google_df[self.global_fields["GEO_LOCATION"]][row]
        address = None if street is None else street + " " + (street_number or '')
        if self.progress_func is not None:
            self.progress_func(name, len(self.google_df))
        self.fill_google_data(row)
        self.fill_cbs_data(city, street)
        self.fill_places_data(geo_location, place_id)
        self.fill_rest_data(name, address, city)
        self.fill_target_data(row)

    def fill_google_data(self, row):
        self.add_data(self.google_config, self.google_df.iloc[row].to_dict())

    def fill_cbs_data(self, city, street):
        self.add_data(self.cbs_config, self.data_filler.get_cbs_data_by_address(city, street))

    def fill_places_data(self, geo_location, place_id):
        self.add_data(self.places_config, self.data_filler.get_places_data_by_point(tuple(geo_location), place_id))

    def fill_rest_data(self, name, address, city):
        name_field = self.global_fields["NAME"]
        address_field = self.global_fields["ADDRESS"]
        g_name_without_common = self.remove_common_words(name)
        first_best = (0.75, None)
        second_best = (0.9, None)
        third_best = (0.6, None)
        forth_best = (2, 0, None)
        for value in self.rest_data.get(city) or []:
            if address is not None and text_distance(address, value[address_field]) > 0.9:
                name_dist = text_distance(name, value[name_field])
                if name_dist > first_best[0]:
                    first_best = (name_dist, value)
                elif second_best[1] is None and name_dist > third_best[0]:
                    third_best = (name_dist, value)

            if first_best[1] is not None:
                continue

            r_name_without_common = self.remove_common_words(value[name_field])
            name_dist_without_common = text_distance(g_name_without_common, r_name_without_common)
            if name_dist_without_common > second_best[0]:
                second_best = (name_dist_without_common, value)

            if second_best[1] is not None or third_best[1] is not None:
                continue

            common_words = self.get_common_words_size(g_name_without_common, r_name_without_common)
            if (len(name.split()) == 1 or len(value[name_field].split()) == 1) and common_words == 1:
                forth_best = (common_words, name_dist_without_common, value)
            elif common_words > forth_best[0] or (common_words == forth_best[0] and name_dist_without_common > forth_best[1]):
                forth_best = (common_words, name_dist_without_common, value)

        self.add_data(self.rest_config, first_best[1] or second_best[1] or third_best[1] or forth_best[2])

    def fill_target_data(self, row):
        rating_data = self.google_df.iloc[row][self.target_field["rating_field"]]
        votes_data = self.google_df.iloc[row][self.target_field["votes_field"]]
        value = self.normalize_votes(votes_data) * rating_data * 20
        self.data[self.target_field["name"]].append(round(value, 3))

    def add_data(self, config, data):
        for field in config["fields"]:
            field_name = field["name"]
            self.data[field_name].append(None if data is None else data[field_name])

    def fill_google_missing_data(self):
        missing_price_level_data = self.google_config["missing_price_level_data"]
        price_level_field = missing_price_level_data["field_name"]
        fill_by_field = missing_price_level_data["fill_by"]
        blank_indexes = [idx for idx, val in enumerate(self.data[price_level_field]) if val is None]
        for blank_idx in blank_indexes:
            self.data[price_level_field][blank_idx] = self.data[fill_by_field][blank_idx]

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
        return location_distance(blank_point, full_point) < 0.5

    def fill_rest_missing_data(self):
        self.fill_rest_missing_kosher_data()
        self.fill_rest_missing_type_data()

    def fill_rest_missing_kosher_data(self):
        missing_kosher_data = self.rest_config["missing_kosher_data"]
        kosher_field = missing_kosher_data["field_name"]
        fill_by_field = missing_kosher_data["fill_by"]
        blank_indexes = [idx for idx, val in enumerate(self.data[kosher_field]) if val is None]
        for blank_idx in blank_indexes:
            if self.data[fill_by_field][blank_idx]:
                self.data[kosher_field][blank_idx] = False

    def fill_rest_missing_type_data(self):
        missing_type_data = self.rest_config["missing_type_data"]
        name_field = self.global_fields["NAME"]
        type_field = missing_type_data["field_name"]
        blank_indexes = [idx for idx, val in enumerate(self.data[type_field]) if val is None]
        for blank_idx in blank_indexes:
            for missing_type_value in missing_type_data["values"]:
                if missing_type_value["contains"] in self.data[name_field][blank_idx]:
                    self.data[type_field][blank_idx] = missing_type_value["fill"]

    def remove_common_words(self, name):
        return " ".join([item for item in name.split(" ") if item not in self.common_words])

    @staticmethod
    def parse_bool_field(value):
        return None if value is None else bool(value)

    @staticmethod
    def get_common_words_size(name1, name2):
        return len(list(set(name1.lower().split(" ")) & set(name2.lower().split(" "))))

    @staticmethod
    def normalize_votes(votes):
        return 1/(1 + np.exp(-0.05 * votes))
