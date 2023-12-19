from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.Operations.RunAlgorithm import RunAlgorithm


class RunAlgorithmWorker(Worker):
    def __init__(self, config_path):
        super(RunAlgorithmWorker, self).__init__(config_path)

    def inner_run(self, config):
        run_algorithm = RunAlgorithm(config, self.progress)
        run_algorithm.pre_run_algo()
        self.emit_pre_build("Run Algorithm...")
        run_algorithm.run_algo()
        self.signals.title.emit("Save Data...")
        run_algorithm.save_data()
        self.signals.title.emit("Run Algorithm Completed!")
