from Client.Workers.Worker import Worker
from Server.DataParser.DataParser import *


class DataParserWorker(Worker):
    def __init__(self, config_path):
        super(DataParserWorker, self).__init__(config_path)

    def inner_run(self, config):
        parser = DataParser(config, self.progress)
        parser.pre_parse_data()
        self.emit_pre_build("Parse Data...")
        parser.parse_data()
        self.signals.title.emit("Fill Missing Data...")
        parser.fill_missing_data()
        self.signals.title.emit("Clean Data...")
        parser.clean_data()
        self.signals.title.emit("Save Data...")
        parser.save_data()
        self.signals.title.emit("Parse Data Completed!")
