from SourceCode.Server.Core.Prediction import *
from SourceCode.Server.Operations.OperationUtils import *
from SourceCode.Server.DataParser.DataParser import DataParser
from SourceCode.Server.Utils.Utils import is_open_on_saturday
import json


class RunPrediction:
    def __init__(self, config, user_selection):
        self.decision_tree_path = config["decision_tree_path"]
        self.data_parser_config_path = config["data_parser_config_path"]
        self.fields = config["fields"]
        self.user_selection = user_selection
        self.formatted_tree = None
        self.tree_input = None

    def set_rest_type(self, rest_type):
        self.user_selection["type"] = rest_type

    def pre_run_prediction(self):
        self.fill_user_data()
        self.get_formatted_tree()
        self.prepare_tree_input()

    def run_prediction(self):
        prediction = Prediction()
        prediction.create_decision_tree(self.formatted_tree)
        return prediction.predict_sample(self.tree_input)

    def fill_user_data(self):
        self.user_selection.update(self.res_calc_features_by_activity())
        self.user_selection.update(self.res_calc_features_by_loc())

    def res_calc_features_by_activity(self):
        friday_activity = [self.user_selection["friday_open"], self.user_selection["friday_close"]]
        saturday_activity = [self.user_selection["saturday_open"], self.user_selection["saturday_close"]]
        data = {"open_on_saturday": is_open_on_saturday(friday_activity, saturday_activity)}
        return data

    def res_calc_features_by_loc(self):
        data = {}
        try:
            with open(self.data_parser_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                data_parser = DataParser(config)
                data_parser.get_places_data()
                data.update(data_parser.get_places_data_by_point(tuple(self.user_selection["geo_location"]), None))
                data_parser.get_cbs_data()
                cbs_data = data_parser.get_cbs_data_by_address(self.user_selection["city"], self.user_selection["street"])
                data.update(cbs_data if cbs_data is not None else {"percent of religious": None, "socio-economic rank": None})
        except IOError:
            print("Error")
        return data

    def prepare_tree_input(self):
        result_as_arr = []
        for field in self.fields:
            if field["type"] == "NUMBER" and isinstance(self.user_selection[field["name"]], str):
                result_as_arr.append(float(self.user_selection[field["name"]]))
            elif isinstance(self.user_selection[field["name"]], list):
                result_as_arr.append(tuple(self.user_selection[field["name"]]))
            else:
                result_as_arr.append(self.user_selection[field["name"]])
        self.tree_input = np.array(result_as_arr.copy(), dtype=object)

    def get_formatted_tree(self):
        try:
            with open(self.decision_tree_path, 'r', encoding='utf-8') as f:
                self.formatted_tree = json.load(f)
        except IOError:
            print("Error")
