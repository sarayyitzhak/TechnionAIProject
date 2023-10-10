from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Algo.RunPrediction import RunPrediction


class RunPredictionWorker(Worker):
    def __init__(self, config_path, user_selection, rest_types):
        super(RunPredictionWorker, self).__init__(config_path, False)
        self.user_selection = user_selection
        self.rest_types = rest_types

    def inner_run(self, config):
        best_prediction = None
        best_user_selection = None
        find_best_rest_type = self.user_selection["type"] is None
        run_prediction = RunPrediction(config, self.user_selection)
        run_prediction.pre_run_prediction()
        if find_best_rest_type:
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

        return {
            "find_best_rest_type": find_best_rest_type,
            "prediction": best_prediction,
            "user_selection": best_user_selection
        }
