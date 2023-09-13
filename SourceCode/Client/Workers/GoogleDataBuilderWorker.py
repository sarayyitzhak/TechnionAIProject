from SourceCode.Client.Workers.Worker import Worker
from SourceCode.Server.DataBuilder.GoogleDataBuilder import GoogleDataBuilder


class GoogleDataBuilderWorker(Worker):
    def __init__(self, config_path):
        super(GoogleDataBuilderWorker, self).__init__(config_path)

    def inner_run(self, config):
        builder = GoogleDataBuilder(config, self.progress)
        self.emit_pre_build("Google Data Builder...")
        builder.build_data()
        self.signals.title.emit("Save Data...")
        builder.save_data()
        self.signals.title.emit("Google Data Builder Completed!")
