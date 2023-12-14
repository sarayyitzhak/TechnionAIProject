from PyQt5.QtCore import *

import time
from SourceCode.Common.FileUtils import *
from SourceCode.Server.Utils.Utils import AppException


class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)
    title = pyqtSignal(str)
    subtitle = pyqtSignal(str)
    actual_time = pyqtSignal(str)
    estimated_time = pyqtSignal(str)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, config_path, delay_after_run=True):
        super(Worker, self).__init__()
        self.config_path = config_path
        self.delay_after_run = delay_after_run
        self.signals = WorkerSignals()
        self.completed_percentage = 0
        self.completed_index = 0
        self.actual_time = 0
        self.start_time = 0
        self.last_time = 0
        self.result = None

    @pyqtSlot()
    def run(self):
        self.signals.title.emit("Read Config File...")
        self.signals.actual_time.emit(f"Actual Time: Calculating...")
        self.signals.estimated_time.emit(f"Estimated Time: Calculating...")
        read_from_file(self.config_path, self.on_config_file_read, self.signals.error.emit, self.on_finished)

    def on_config_file_read(self, config):
        try:
            self.result = self.inner_run(config)
        except AppException as e:
            self.signals.error.emit(("An error occurred", e.msg))

        self.post_inner_run()
        if self.delay_after_run:
            time.sleep(2)

    def inner_run(self, config):
        pass

    def post_inner_run(self):
        self.signals.subtitle.emit("")
        self.signals.progress.emit(100)

    def on_finished(self):
        self.signals.finished.emit(self.result)

    def emit_pre_build(self, title):
        self.signals.title.emit(title)
        self.completed_percentage = 0
        self.completed_index = 0
        self.actual_time = 0
        self.start_time = time.time()
        self.last_time = self.start_time

    def progress(self, name, total):
        self.completed_index += 1
        total = max(total, self.completed_index)
        self.calculate_actual_time()
        self.calculate_estimated_time(total)
        self.signals.subtitle.emit(f"Name: ({self.completed_index}/{total}) {name}")
        if int((self.completed_index / total) * 100) >= self.completed_percentage:
            self.signals.progress.emit(self.completed_percentage)
            self.completed_percentage += 1

    def calculate_actual_time(self):
        current_time = time.time()
        secs = int(current_time - self.start_time)
        if secs > self.actual_time:
            minutes = int(secs / 60)
            if minutes == 0:
                self.signals.actual_time.emit(f"Actual Time: {secs} seconds")
            else:
                self.signals.actual_time.emit(f"Actual Time: {minutes} m {secs - (minutes * 60)} s")
            self.actual_time = secs

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
