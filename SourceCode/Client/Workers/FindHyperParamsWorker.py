from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Algo.FindHyperParams import FindHyperParams


class FindHyperParamsWorker(Worker):
    def __init__(self, config_path):
        super(FindHyperParamsWorker, self).__init__(config_path)

    def inner_run(self, config):
        parser = FindHyperParams(config, self.progress)
        parser.pre_find_hyper_params()
        self.emit_pre_build("Find Hyper Params...")
        parser.find_hyper_params()
        self.signals.title.emit("Save Data...")
        parser.save_data()
        self.signals.title.emit("Find Hyper Params Completed!")
