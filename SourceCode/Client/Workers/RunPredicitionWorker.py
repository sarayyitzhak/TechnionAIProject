from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Operations.OperationUtils import *
from SourceCode.Server.Operations.RunPrediction import RunPrediction


class RunPredictionWorker(Worker):
    def __init__(self, config_path, user_selection, rest_types, find_best_rest_type):
        super(RunPredictionWorker, self).__init__(config_path, False)
        self.user_selection = user_selection
        self.rest_types = rest_types
        self.find_best_rest_type = find_best_rest_type

    def inner_run(self, config):
        best_prediction = None
        best_user_selection = None
        run_prediction = RunPrediction(config, self.user_selection)
        run_prediction.pre_run_prediction()
        if self.find_best_rest_type:
            for rest_type in self.rest_types:
                run_prediction.set_rest_type(rest_type)
                run_prediction.prepare_tree_input()
                prediction = run_prediction.run_prediction()
                if best_prediction is None or prediction.value > best_prediction.value:
                    best_prediction = prediction
                    best_user_selection = run_prediction.user_selection
        else:
            best_prediction = run_prediction.run_prediction()
            best_user_selection = run_prediction.user_selection

        same_type_count = get_same_type_count(config["data_set_path"], best_user_selection)
        rest_count, rest_pos = get_rate_position(config["data_set_path"], best_prediction.value, best_user_selection["geo_location"])

        return {
            "prediction": best_prediction,
            "find_best_rest_type": self.find_best_rest_type,
            "user_selection": best_user_selection,
            "same_type_count": same_type_count,
            "rest_count": rest_count,
            "rest_pos": rest_pos
        }
