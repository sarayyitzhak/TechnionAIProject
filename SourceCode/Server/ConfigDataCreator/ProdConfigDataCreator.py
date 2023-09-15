from SourceCode.Server.Algo.ID3 import *
from SourceCode.Server.Utils.FileUtils import *


class ProdConfigDataCreator:

    def __init__(self, config):
        self.data_set_path = config["data_set_path"]
        self.output_path = config["output_path"]
        self.config_data = None

    def create_prod_config_data(self):
        data = pd.read_csv(self.data_set_path)
        rest_types = sorted(data["type"].dropna().unique())
        price_levels = sorted(data["price_level"].dropna().unique())
        self.config_data = {
            "type": rest_types,
            "price_level": [str(int(price_level)) for price_level in price_levels]
        }

    def save_data(self):
        write_to_file(self.config_data, self.output_path)

