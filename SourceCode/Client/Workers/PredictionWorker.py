from PyQt5 import QtCore

from SourceCode.Client.Screens.ProdClientLoadingScreen import *
from SourceCode.Server.Algo.ID3Experiments import *
import time
from PyQt5.QtCore import pyqtSignal, QObject

from SourceCode.Server.Algo.Prediction import Prediction
from SourceCode.Server.DataFiller import *


class PredictionWorker(QThread):

    finished = QtCore.pyqtSignal(str)

    def __init__(self, user_selection):
        super().__init__()
        self.user_selection = user_selection
        self.algo_input = None
        self.data_filler = None
        self.pred = None
        self.rate = 0
        config_file = open('./ConfigFiles/prediction-config.json', 'r', encoding='utf-8')
        self.config = json.load(config_file)
        self.fields = self.config["fields"]
        tree_file = open('./DataOutput/algo-tree.json', 'r', encoding='utf-8')
        self.formatted_tree = json.load(tree_file)
        self.fill_user_data()

    def fill_user_data(self):
        self.user_selection.update(self.res_calc_features_by_activity())
        self.user_selection.update(self.res_calc_features_by_loc())

    def res_calc_features_by_activity(self):
        data = {}
        activity_hours = self.user_selection["activity_time_as_list"]
        for is_open, mean in enumerate(["open_activity_hour", "close_activity_hour"]):
            data[mean] = ActivityTimeFiller.get_most_common_activity_hour(activity_hours, 1 - is_open)
        data["open_on_saturday"] = ActivityTimeFiller.is_open_on_saturday(activity_hours)
        return data

    def res_calc_features_by_loc(self):
        data = {}
        config_file = open('./ConfigFiles/data-parser-config.json', 'r', encoding='utf-8')
        self.data_filler = DataFiller(json.load(config_file))
        self.data_filler.get_places_data()
        data.update(self.data_filler.get_places_data_by_point(tuple(self.user_selection["geo_location"]), None))
        self.data_filler.get_cbs_data()
        cbs_data = self.data_filler.get_cbs_data_by_address(self.user_selection["city"], self.user_selection["street"])
        data.update(cbs_data if cbs_data is not None else {})
        return data

    def run_alg(self):
        self.pre_run_algo()
        self.pred = Prediction()
        self.pred.create_decision_tree(self.formatted_tree)
        self.rate = self.pred.predict_sample(self.algo_input, False)
        self.finished.emit(str(self.rate))

    def pre_run_algo(self):
        result_as_arr = []
        for field in self.fields:
            if field["name"] in self.user_selection:
                if isinstance(self.user_selection[field["name"]], list):
                    result_as_arr.append(tuple(self.user_selection[field["name"]]))
                else:
                    result_as_arr.append(self.user_selection[field["name"]])
        self.algo_input = np.array(result_as_arr.copy(), dtype=object)

