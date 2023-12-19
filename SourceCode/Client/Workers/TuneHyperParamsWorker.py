from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Operations.TuneHyperParams import TuneHyperParams


class TuneHyperParamsWorker(Worker):
    def __init__(self, config_path):
        super(TuneHyperParamsWorker, self).__init__(config_path)

    def inner_run(self, config):
        find_hyper_params = TuneHyperParams(config, self.progress)
        find_hyper_params.pre_find_hyper_params()
        self.emit_pre_build("Find Hyper Params...")
        find_hyper_params.find_hyper_params()
        self.signals.title.emit("Save Data...")
        find_hyper_params.save_data()
        self.signals.title.emit("Find Hyper Params Completed!")
