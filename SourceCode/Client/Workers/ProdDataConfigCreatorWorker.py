from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.ConfigDataCreator.ProdDataConfigCreator import *


class ProdDataConfigCreatorWorker(Worker):
    def __init__(self, config_path):
        super(ProdDataConfigCreatorWorker, self).__init__(config_path)

    def inner_run(self, config):
        creator = ProdDataConfigCreator(config)
        self.emit_pre_build("Create Config Data...")
        creator.create_prod_config_data()
        self.signals.title.emit("Save Data...")
        creator.save_data()
        self.signals.title.emit("Create Config Data Completed!")
