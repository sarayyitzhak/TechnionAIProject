from PyQt5.QtCore import *

from Server.DataBuilder.RestDataBuilder import RestDataBuilder
import json
import traceback
import sys
import time


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    title = pyqtSignal(str)
    subtitle = pyqtSignal(str)
    estimated_time = pyqtSignal(str)
    progress = pyqtSignal(int)


class RestDataBuilderWorker(QRunnable):
    def __init__(self):
        super(RestDataBuilderWorker, self).__init__()
        self.signals = WorkerSignals()
        self.completed = 0
        self.start_time = 0
        self.last_time = 0

    @pyqtSlot()
    def run(self):
        try:
            with open('./Server/DataConfig/rest-data-config.json', 'r', encoding='utf-8') as f:
                builder = RestDataBuilder(json.load(f), self.progress)
                self.signals.title.emit("Rest Data Builder...")
                self.signals.estimated_time.emit(f"Estimated Time: Calculating...")
                builder.pre_build_data()
                self.start_time = time.time()
                self.last_time = self.start_time
                builder.build_data()
                self.signals.title.emit("Save Data...")
                builder.save_data()
                self.signals.title.emit("Rest Data Builder Completed!")
        except:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((str(exctype), str(value), str(traceback.format_exc())))
        finally:
            time.sleep(2)
            self.signals.finished.emit()

    def progress(self, name, index, total):
        self.calculate_estimated_time(index, total)
        self.signals.subtitle.emit(f"Name: ({index}/{total}) {name}")
        if int((index / total) * 100) >= self.completed:
            self.signals.progress.emit(self.completed)
            self.completed += 1

    def calculate_estimated_time(self, index, total):
        if index > 10:
            current_time = time.time()
            if int(current_time - self.last_time) > 0:
                time_diff = current_time - self.start_time
                secs = int(((total - index) / index) * time_diff)
                minutes = int(secs / 60)
                if minutes == 0:
                    self.signals.estimated_time.emit(f"Estimated Time: {secs} seconds")
                else:
                    self.signals.estimated_time.emit(f"Estimated Time: {minutes} m {secs - (minutes * 60)} s")
                self.last_time = current_time
