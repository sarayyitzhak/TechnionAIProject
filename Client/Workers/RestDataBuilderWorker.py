from Client.Workers.Worker import Worker
from Server.DataBuilder.RestDataBuilder import RestDataBuilder


class RestDataBuilderWorker(Worker):
    def __init__(self, config_path):
        super(RestDataBuilderWorker, self).__init__(config_path)

    def inner_run(self, config):
        builder = RestDataBuilder(config, self.progress)
        builder.pre_build_data()
        self.emit_pre_build("Rest Data Builder...")
        builder.build_data()
        self.signals.title.emit("Save Data...")
        builder.save_data()
        self.signals.title.emit("Rest Data Builder Completed!")
