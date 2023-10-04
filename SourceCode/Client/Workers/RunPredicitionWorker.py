from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Algo.RunPrediction import RunPrediction


class RunPredictionWorker(Worker):
    def __init__(self, config_path, user_selection):
        super(RunPredictionWorker, self).__init__(config_path)
        self.user_selection = user_selection

    def inner_run(self, config):
        run_prediction = RunPrediction(config, self.user_selection)
        run_prediction.pre_run_prediction()
        prediction = run_prediction.run_prediction()
        self.signals.finished.emit(prediction.value)
