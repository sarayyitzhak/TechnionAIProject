from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback
import sys


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(str)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.completed = 0

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        self.fn(self.progress)
        # try:
        #     result = self.fn(*self.args, **self.kwargs)
        # except:
        #     traceback.print_exc()
        #     exctype, value = sys.exc_info()[:2]
        #     self.signals.error.emit((exctype, value, traceback.format_exc()))
        # else:
        #     self.signals.result.emit(result)  # Return the result of the processing
        # finally:
        #     self.signals.finished.emit()  # Done

    def progress(self, name, index, total):
        if index == total:
            self.signals.result.emit("Parsing Data Completed!")
        else:
            self.signals.result.emit(f"Parsing Data...\n({index}/{total}) {name}")

        if int((index / total) * 100) >= self.completed:
            self.signals.progress.emit(self.completed)
            self.completed += 1
