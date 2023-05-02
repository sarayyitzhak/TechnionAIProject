from Client.Worker import Worker
from Server.DataBuilder.GovDataBuilder import GovDataBuilder


class GovDataBuilderWorker(Worker):
    def __init__(self, config_path):
        super(GovDataBuilderWorker, self).__init__(config_path)

    def inner_run(self, config):
        builder = GovDataBuilder(config, self.progress)
        builder.pre_build_data()
        self.emit_pre_build("Gov Data Builder...")
        builder.build_data()
        self.signals.title.emit("Save Data...")
        builder.save_data()
        self.signals.title.emit("Gov Data Builder Completed!")
