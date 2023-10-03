from SourceCode.Client.Screens.ProdClientLoadingScreen import *
from SourceCode.Server.Algo.ID3Experiments import *
from SourceCode.Server.Algo.Prediction import Prediction
from SourceCode.Server.DataParser.DataFiller import *

from PyQt5 import QtCore


class PredictionWorker(QThread):

    finished = QtCore.pyqtSignal(float)

    def __init__(self, user_selection):
        super().__init__()
        self.user_selection = user_selection
        self.algo_input = None
        self.data_filler = None
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
        friday_activity = [self.user_selection["friday_open"], self.user_selection["friday_close"]]
        saturday_activity = [self.user_selection["saturday_open"], self.user_selection["saturday_close"]]
        data = {"open_on_saturday": ActivityTimeFiller.is_open_on_saturday(friday_activity, saturday_activity)}
        return data

    def res_calc_features_by_loc(self):
        data = {}
        config_file = open('./ConfigFiles/data-parser-config.json', 'r', encoding='utf-8')
        self.data_filler = DataFiller(json.load(config_file))
        self.data_filler.get_places_data()
        data.update(self.data_filler.get_places_data_by_point(tuple(self.user_selection["geo_location"]), None))
        self.data_filler.get_cbs_data()
        cbs_data = self.data_filler.get_cbs_data_by_address(self.user_selection["city"], self.user_selection["street"])
        data.update(cbs_data if cbs_data is not None else {"percent of religious": None, "socio-economic rank": None})
        return data

    def pre_run_algo(self):
        result_as_arr = []
        for field in self.fields:
            if field["type"] == "NUMBER" and isinstance(self.user_selection[field["name"]], str):
                result_as_arr.append(float(self.user_selection[field["name"]]))
            elif isinstance(self.user_selection[field["name"]], list):
                result_as_arr.append(tuple(self.user_selection[field["name"]]))
            else:
                result_as_arr.append(self.user_selection[field["name"]])
        self.algo_input = np.array(result_as_arr.copy(), dtype=object)

    def run_alg(self):
        self.pre_run_algo()
        prediction = Prediction()
        prediction.create_decision_tree(self.formatted_tree)
        rate = prediction.predict_sample(self.algo_input).value
        self.finished.emit(rate)
