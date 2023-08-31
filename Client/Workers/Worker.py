from PyQt5.QtCore import *

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


class Worker(QRunnable):
    def __init__(self, config_path):
        super(Worker, self).__init__()
        self.config_path = config_path
        self.signals = WorkerSignals()
        self.completed_percentage = 0
        self.completed_index = 0
        self.start_time = 0
        self.last_time = 0

    @pyqtSlot()
    def run(self):
        self.signals.title.emit("Read Config File...")
        self.signals.estimated_time.emit(f"Estimated Time: Calculating...")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.inner_run(json.load(f))
                self.post_inner_run()
                time.sleep(2)
        except:
            print(traceback.format_exc())
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((str(exctype), str(value), str(traceback.format_exc())))
        finally:
            self.signals.finished.emit()

    def inner_run(self, config):
        pass

    def post_inner_run(self):
        self.signals.subtitle.emit("")
        self.signals.progress.emit(100)

    def emit_pre_build(self, title):
        self.signals.title.emit(title)
        self.completed_percentage = 0
        self.completed_index = 0
        self.start_time = time.time()
        self.last_time = self.start_time

    def progress(self, name, total):
        self.completed_index += 1
        total = max(total, self.completed_index)
        self.calculate_estimated_time(total)
        self.signals.subtitle.emit(f"Name: ({self.completed_index}/{total}) {name}")
        if int((self.completed_index / total) * 100) >= self.completed_percentage:
            self.signals.progress.emit(self.completed_percentage)
            self.completed_percentage += 1

    def calculate_estimated_time(self, total):
        if self.completed_index > 10:
            current_time = time.time()
            if int(current_time - self.last_time) > 0:
                time_diff = current_time - self.start_time
                secs = int(((total - self.completed_index) / self.completed_index) * time_diff)
                minutes = int(secs / 60)
                if minutes == 0:
                    self.signals.estimated_time.emit(f"Estimated Time: {secs} seconds")
                else:
                    self.signals.estimated_time.emit(f"Estimated Time: {minutes} m {secs - (minutes * 60)} s")
                self.last_time = current_time
