from Client.Worker import Worker
from Server.DataBuilder.CbsDataBuilder import CbsDataBuilder


class CbsDataBuilderWorker(Worker):
    def __init__(self, config_path):
        super(CbsDataBuilderWorker, self).__init__(config_path)

    def inner_run(self, config):
        builder = CbsDataBuilder(config, self.progress)
        builder.pre_build_data()
        self.emit_pre_build("Religious Data Builder...")
        builder.build_religious_data()
        self.emit_pre_build("Socio Economic Data Builder...")
        builder.build_socio_economic_data()
        self.emit_pre_build("CBS Data Builder...")
        builder.build_data()
        self.signals.title.emit("Save Data...")
        builder.save_data()
        self.signals.title.emit("CBS Data Builder Completed!")
