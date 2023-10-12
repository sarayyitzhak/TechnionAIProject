from SourceCode.Common.FileUtils import *
import pandas as pd


class ProdDataConfigCreator:

    def __init__(self, config):
        self.data_set_path = config["data_set_path"]
        self.cbs_data_set_path = config["cbs_data_set_path"]
        self.output_path = config["output_path"]
        self.config_data = {}

    def create_prod_config_data(self):
        self.set_config_by_data()
        self.set_config_by_cbs_data()

    def save_data(self):
        write_to_file(self.config_data, self.output_path)

    def set_config_by_data(self):
        data = pd.read_csv(self.data_set_path)
        rest_types = sorted(data["type"].dropna().unique())
        price_levels = sorted(data["price_level"].dropna().unique())
        self.config_data["type"] = rest_types
        self.config_data["price_level"] = [str(int(price_level)) for price_level in price_levels]

    def set_config_by_cbs_data(self):
        cbs_data = pd.read_csv(self.cbs_data_set_path)
        self.config_data["city_streets"] = {}
        city_groups = cbs_data.groupby("city")
        for city in city_groups.groups.keys():
            self.config_data["city_streets"][city] = sorted(list(city_groups.get_group(city)["street"]))
