from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.ConfigDataCreator.ProdConfigDataCreator import *


class ProdConfigDataCreatorWorker(Worker):
    def __init__(self, config_path):
        super(ProdConfigDataCreatorWorker, self).__init__(config_path)

    def inner_run(self, config):
        creator = ProdConfigDataCreator(config)
        self.emit_pre_build("Create Config Data...")
        creator.create_prod_config_data()
        self.signals.title.emit("Save Data...")
        creator.save_data()
        self.signals.title.emit("Create Config Data Completed!")
