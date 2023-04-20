from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Server.DataBuilder import RestDataBuilder, CbsDataBuilder, GovDataBuilder, GoogleDataBuilder
from Server.DataParser import DataParser
from Server.Algo import RunAlgorithm
from Client.Workers import *


class DevClientMainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')

        self.setWindowTitle("Restaurant Rating Predictor")

        self.threadpool = QThreadPool()

        self.layout = QGridLayout()

        self.build_buttons()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_label = None

        self.setLayout(self.layout)
        self.layout.setContentsMargins(50, 50, 50, 50)

    def build_buttons(self):
        self.build_button(0, 0, 1, "Build Google data", self.on_build_google_button_clicked)
        self.build_button(0, 1, 1, "Build Rest data", self.on_build_rest_button_clicked)
        self.build_button(0, 2, 1, "Build CBS data", self.on_build_cbs_button_clicked)
        self.build_button(0, 3, 1, "Build Gov data", self.on_build_gov_button_clicked)
        self.build_button(1, 0, 4, "Build all data", self.on_build_all_button_clicked)
        self.build_button(2, 0, 4, "Parse data", self.on_parse_data_button_clicked)
        self.build_button(3, 0, 4, "Run algorithm", self.on_run_alg_button_clicked)

    def build_button(self, i, j, width, label, function):
        button = QPushButton(label)
        self.layout.addWidget(button, i, j, 1, width)
        button.clicked.connect(function)

    def build_progress_bar(self):
        self.layout.addWidget(self.progress_label, 4, 0, 1, 4)
        self.progress_label.show()
        self.layout.addWidget(self.progress_bar, 5, 0, 1, 4)
        self.progress_bar.show()

    @staticmethod
    def on_build_google_button_clicked():
        GoogleDataBuilder.google_build_data()

    @staticmethod
    def on_build_rest_button_clicked():
        RestDataBuilder.rest_build_data()

    @staticmethod
    def on_build_cbs_button_clicked():
        CbsDataBuilder.cbs_build_data()

    @staticmethod
    def on_build_gov_button_clicked():
        GovDataBuilder.gov_build_data()

    @staticmethod
    def on_build_all_button_clicked():
        GoogleDataBuilder.google_build_data()
        RestDataBuilder.rest_build_data()
        CbsDataBuilder.cbs_build_data()
        GovDataBuilder.gov_build_data()

    # @staticmethod
    def on_parse_data_button_clicked(self):
        self.progress_label = QLabel("Parsing Data...")
        self.build_progress_bar()

        worker = Worker(DataParser.parse_data)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.result.connect(self.print_output)

        self.threadpool.start(worker)

    def progress_fn(self, p):
        self.progress_bar.setValue(int(p))
        if self.progress_bar.value() == 100:
            time.sleep(2)
            self.progress_bar.hide()
            self.progress_label.hide()

    def print_output(self, value):
        self.progress_label.setText(value)

    def on_run_alg_button_clicked(self):
        self.build_progress_bar()
        RunAlgorithm.run_alg()
