import math
import json
import pandas as pd
from Server.DataBuilder.Utils import write_to_file, write_dict_to_file

# pip install xlrd
# pip install openpyxl


class CbsDataBuilder:
    def __init__(self, config, progress_func):
        self.religious_config = config["religious"]
        self.transition_key_config = config["transition"]
        self.streets_config = config["streets"]
        self.ser_config = config["ser"]
        self.cities_config = config["cities"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.religious_df = None
        self.ser_df = None
        self.transition_key_df = None
        self.streets_df = None
        self.rel_by_street_df = None
        self.rel_by_street_count = None
        self.ser_by_street_df = None
        self.ser_by_street_count = None
        self.streets_dict = {}
        self.data = []

    def pre_build_data(self):
        self.get_data_frames()
        self.prepare_data()
        self.rel_by_street_df = self.join_data_frames(self.religious_df, self.religious_config)
        self.ser_by_street_df = self.join_data_frames(self.ser_df, self.ser_config)
        self.rel_by_street_count = self.get_street_count(self.rel_by_street_df, 0, 2)
        self.ser_by_street_count = self.get_street_count(self.ser_by_street_df, 0, 4)
        self.streets_df = self.streets_df.iloc[:, [0, 4]].copy()
        self.init_street_dict()

    def build_religious_data(self):
        self.add_religious_to_dict()

    def build_socio_economic_data(self):
        self.add_ser_to_dict()

    def build_data(self):
        self.data_dict_to_list()

    def save_data(self):
        pd.DataFrame(self.data).to_csv(self.output_path, index=False, encoding='utf-8-sig')

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
        return df_by_street[df_by_street['רחובות עיקריים'].notna()].reset_index(drop=True)

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
            for city, street in self.get_city_street_list(self.rel_by_street_df, row, 0, 2):
                people_count = self.rel_by_street_df.iloc[:, 3][row]
                religions_count = self.rel_by_street_df.iloc[:, 4][row]
                if religions_count == '..':
                    religions_count = 0
                if self.streets_dict[(street, city)]["amount of people"] is None:
                    self.init_rel_by_street(street, city)
                self.update_rel_by_street(street, city, people_count, religions_count)
                if self.progress_func is not None:
                    self.progress_func(f"{street}, {city}", self.rel_by_street_count)

    def add_ser_to_dict(self):
        for row in range(len(self.ser_by_street_df)):
            for city, street in self.get_city_street_list(self.ser_by_street_df, row, 0, 4):
                index_value = self.ser_by_street_df.iloc[:, 1][row]
                rank = self.ser_by_street_df.iloc[:, 2][row]
                cluster = self.ser_by_street_df.iloc[:, 3][row]
                if self.streets_dict[(street, city)]["socio-economic index value"] is None:
                    self.init_ser_by_street(street, city)
                self.update_ser_by_street(street, city, index_value, rank, cluster)
                if self.progress_func is not None:
                    self.progress_func(f"{street}, {city}", self.ser_by_street_count)

    def data_dict_to_list(self):
        for street, city in self.streets_dict.keys():
            value = self.streets_dict[(street, city)]
            percent_of_religious, index_value_avg, rank_avg, cluster_avg = None, None, None, None
            if value["amount of religious"] is not None:
                percent_of_religious = round((value["amount of religious"] / value["amount of people"]) * 100, 2)
            socio_economic_counter = value["socio-economic counter"]
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
            if self.progress_func is not None:
                self.progress_func(f"{street}, {city}", len(self.streets_dict))

    def get_street_count(self, df, city_col, street_col):
        return sum([len(self.get_city_street_list(df, row, city_col, street_col)) for row in range(len(df))])

    def get_city_street_list(self, df, row, city_col, street_col):
        city = df.iloc[:, city_col][row]
        streets = df.iloc[:, street_col][row]
        if city in self.cities_config["city_names"] and isinstance(streets, str):
            return [(city, street.replace("שד", "שדרות")) for street in streets.split(', ')]
        return []

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
        self.streets_dict[(street, city)]["socio-economic index value"] += index_value
        self.streets_dict[(street, city)]["socio-economic rank"] += rank
        self.streets_dict[(street, city)]["socio-economic cluster"] += cluster
        self.streets_dict[(street, city)]["socio-economic counter"] += 1

    def init_rel_by_street(self, street, city):
        self.streets_dict[(street, city)]["amount of people"] = 0
        self.streets_dict[(street, city)]["amount of religious"] = 0

    def update_rel_by_street(self, street, city, people_count, religions_count):
        self.streets_dict[(street, city)]["amount of people"] += people_count
        self.streets_dict[(street, city)]["amount of religious"] += religions_count


def cbs_build_data():
    try:
        with open('./Server/DataConfig/cbs-data-config.json', 'r', encoding='utf-8') as f:
            builder = CbsDataBuilder(json.load(f), None)
            builder.pre_build_data()
            builder.build_religious_data()
            builder.build_socio_economic_data()
            builder.build_data()
            builder.save_data()
    except IOError:
        print("Error")
