from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Algo.RunAlgorithm import RunAlgorithm


class RunAlgorithmWorker(Worker):
    def __init__(self, config_path):
        super(RunAlgorithmWorker, self).__init__(config_path)

    def inner_run(self, config):
        algo = RunAlgorithm(config, self.progress)
        algo.pre_run_algo()
        self.emit_pre_build("Run Algorithm...")
        algo.run_algo()
        self.signals.title.emit("Save Data...")
        algo.save_data()
        self.signals.title.emit("Run Algorithm Completed!")
