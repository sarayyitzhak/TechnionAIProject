import math
import json
import pandas as pd
from Server.DataBuilder.Utils import write_to_file, write_dict_to_file

# pip install xlrd
# pip install openpyxl


class CbsDataBuilder:
    def __init__(self, religious_config, transition_key_config, streets_config, ser_config, cities_config):
        self.religious_config = religious_config
        self.transition_key_config = transition_key_config
        self.streets_config = streets_config
        self.ser_config = ser_config
        self.cities_config = cities_config
        self.religious_df = None
        self.transition_key_df = None
        self.streets_df = None
        self.ser_df = None
        self.rel_by_street_df = None
        self.ser_by_street_df = None
        self.streets_dict = {}
        self.data = []

    def build_data(self):
        self.get_data_frames()
        self.prepare_data()
        self.rel_by_street_df = self.join_data_frames(self.religious_df, self.religious_config)
        self.ser_by_street_df = self.join_data_frames(self.ser_df, self.ser_config)
        self.streets_df = self.streets_df.iloc[:, [0, 4]].copy()
        self.init_street_dict()
        self.add_religious_to_dict()
        self.add_ser_to_dict()
        self.data_dict_to_list()

    def get_data_frames(self):
        self.religious_df = self.get_data_frame(self.religious_config)
        self.transition_key_df = self.get_data_frame(self.transition_key_config)
        self.streets_df = self.get_data_frame(self.streets_config)
        self.ser_df = self.get_data_frame(self.ser_config)

    @staticmethod
    def get_data_frame(config):
        return pd.read_excel(config["file"], sheet_name=config["sheet_name"], skiprows=config["rows_to_skip"],
                             usecols=config["columns"])

    @staticmethod
    def str_col_to_int(col):
        for i in range(len(col)):
            if col[i].isnumeric():
                col[i] = int(col[i])
        return col

    def prepare_data(self):
        self.ser_df.columns = self.ser_config["columns_names"]
        self.religious_df.reset_index(drop=True)
        for idx in [0, 2]:
            self.transition_key_df.iloc[:, idx] = self.str_col_to_int(self.transition_key_df.iloc[:, idx])
        for row in range(len(self.streets_df)):
            self.streets_df.iloc[:, 0] = self.streets_df.iloc[:, 0].replace(self.cities_config["city_names_to_replace"]["old"],
                                                                            self.cities_config["city_names_to_replace"]["new"])

    def join_data_frames(self, df, df_config):
        df_by_street_raw = df.merge(self.transition_key_df, how='left',
                                           left_on=[df.keys()[0], df.keys()[2]],
                                           right_on=[self.transition_key_df.keys()[0], self.transition_key_df.keys()[2]])
        df_by_street_raw = df_by_street_raw.merge(self.streets_df, how='left',
                                                        left_on=df_by_street_raw.keys()[12],
                                                        right_on=self.streets_df.keys()[1])
        df_by_street = df_by_street_raw.iloc[:, df_config["columns_idxes_to_use"]].copy()
        x = df_by_street[df_by_street['רחובות עיקריים'].notna()].reset_index(drop=True)
        return x

    def init_street_dict(self, ):
        for row in range(len(self.streets_df)):
            city = self.streets_df.iloc[:, 0][row]
            if city in self.cities_config["city_names"] and isinstance(self.streets_df.iloc[:, 1][row], str):
                streets_list = self.get_streets(row)
                for street in streets_list:
                    key_in_dict = self.streets_dict.get((street, city))
                    if key_in_dict is None:
                        self.add_to_dict(street, city)

    def get_streets(self, row):
        streets_list = self.streets_df.iloc[:, 1][row].split(', ')
        return [street.replace("שד", "שדרות") for street in streets_list]

    def add_to_dict(self, street, city):
        self.streets_dict[(street, city)] = {
            "amount of people": None,
            "amount of religious": None,
            "socio-economic index value": None,
            "socio-economic rank": None,
            "socio-economic cluster": None,
            "socio-economic counter": None
        }

    def add_religious_to_dict(self):
        for row in range(len(self.rel_by_street_df)):
            city = self.rel_by_street_df.iloc[:, 0][row]
            streets = self.rel_by_street_df.iloc[:, 2][row]
            if city in self.cities_config["city_names"] and isinstance(streets, str):
                streets_list = self.get_streets_list(streets)
                people_count = self.rel_by_street_df.iloc[:, 3][row]
                religions_count = self.rel_by_street_df.iloc[:, 4][row]
                if religions_count == '..':
                    religions_count = 0
                for street in streets_list:
                    if self.streets_dict[(street, city)]["amount of people"] is None:
                        self.init_rel_by_street(street, city)
                    self.update_rel_by_street(street, city, people_count, religions_count)

    def add_ser_to_dict(self):
        for row in range(len(self.ser_by_street_df)):
            city = self.ser_by_street_df.iloc[:, 0][row]
            streets = self.ser_by_street_df.iloc[:, 4][row]
            if city in self.cities_config["city_names"] and isinstance(streets, str):
                streets_list = self.get_streets_list(streets)
                index_value = self.ser_by_street_df.iloc[:, 1][row]
                rank = self.ser_by_street_df.iloc[:, 2][row]
                cluster = self.ser_by_street_df.iloc[:, 3][row]
                for street in streets_list:
                    if self.streets_dict[(street, city)]["socio-economic index value"] is None:
                        self.init_ser_by_street(street, city)
                    self.update_ser_by_street(street, city, index_value, rank, cluster)

    def data_dict_to_list(self):
        for street, city in self.streets_dict.keys():
            value = self.streets_dict[(street, city)]
            socio_economic_counter = value["socio-economic counter"]
            percent_of_religious = None if value["amount of religious"] is None else round(
                (value["amount of religious"] / value["amount of people"]) * 100, 2)
            index_value_avg, rank_avg, cluster_avg = None, None, None
            if socio_economic_counter is not None:
                index_value_avg = round(value["socio-economic index value"] / socio_economic_counter, 3)
                rank_avg = round(value["socio-economic rank"] / socio_economic_counter, 3)
                cluster_avg = round(value["socio-economic cluster"] / socio_economic_counter, 3)

            self.data.append({
                "city": city,
                "street": street,
                "percent of religious": percent_of_religious,
                "socio-economic index value": index_value_avg,
                "socio-economic rank": rank_avg,
                "socio-economic cluster": cluster_avg
            })

    @staticmethod
    def get_streets_list(streets):
        streets_list = streets.split(', ')
        return [street.replace("שד", "שדרות") for street in streets_list]

    def init_ser_by_street(self, street, city):
        self.streets_dict[(street, city)]["socio-economic index value"] = 0
        self.streets_dict[(street, city)]["socio-economic rank"] = 0
        self.streets_dict[(street, city)]["socio-economic cluster"] = 0
        self.streets_dict[(street, city)]["socio-economic counter"] = 0

    def update_ser_by_street(self, street, city, index_value, rank, cluster):
        previous_data = self.streets_dict[(street, city)]
        self.streets_dict[(street, city)]["socio-economic index value"] = round(
            (previous_data["socio-economic index value"] + index_value) / 2, 3)
        self.streets_dict[(street, city)]["socio-economic rank"] = (previous_data["socio-economic rank"] + rank) / 2
        self.streets_dict[(street, city)]["socio-economic cluster"] = (previous_data[
                                                                           "socio-economic cluster"] + cluster) / 2
        self.streets_dict[(street, city)]["socio-economic counter"] = previous_data["socio-economic counter"] + 1

    def init_rel_by_street(self, street, city):
        self.streets_dict[(street, city)]["amount of people"] = 0
        self.streets_dict[(street, city)]["amount of religious"] = 0

    def update_rel_by_street(self, street, city, people_count, religions_count):
        previous_data = self.streets_dict[(street, city)]
        self.streets_dict[(street, city)]["amount of people"] = previous_data["amount of people"] + people_count
        self.streets_dict[(street, city)]["amount of religious"] = previous_data[
                                                                       "amount of religious"] + religions_count


def build_data_3():
    try:
        with open('./DataConfig/cbs-data-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            builder = CbsDataBuilder(config["religious"], config["transition"], config["streets"], config["ser"], config["cities"])
            builder.build_data()
            write_to_file(builder.data, config["output_path"])
    except IOError:
        print("Error")
