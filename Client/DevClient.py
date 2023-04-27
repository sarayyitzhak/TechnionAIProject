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
from Client.DataParserWorker import *


class DevClientMainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')

        self.setWindowTitle("Restaurant Rating Predictor")

        self.thread_pool = QThreadPool()

        self.layout = QGridLayout()

        self.progress_bar = None
        self.title = None
        self.subtitle = None
        self.estimated_time = None

        self.build_buttons()
        self.build_progress_bar()
        self.hide_progress_bar()

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
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.title = QLabel()
        self.subtitle = QLabel()
        self.estimated_time = QLabel()

        self.layout.addWidget(self.title, 4, 0, 1, 4)
        self.layout.addWidget(self.subtitle, 5, 0, 1, 4)
        self.layout.addWidget(self.progress_bar, 6, 0, 1, 4)
        self.layout.addWidget(self.estimated_time, 7, 0, 1, 4)

    def show_progress_bar(self):
        self.progress_bar.show()
        self.title.show()
        self.subtitle.show()
        self.estimated_time.show()

    def hide_progress_bar(self):
        self.progress_bar.hide()
        self.title.hide()
        self.subtitle.hide()
        self.estimated_time.hide()

    def set_progress(self, p):
        self.progress_bar.setValue(int(p))

    def set_title(self, value):
        self.title.setText(value)

    def set_subtitle(self, value):
        self.subtitle.setText(value)

    def set_estimated_time(self, value):
        self.estimated_time.setText(value)

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

    def on_parse_data_button_clicked(self):
        self.show_progress_bar()

        worker = DataParserWorker()
        worker.signals.progress.connect(self.set_progress)
        worker.signals.title.connect(self.set_title)
        worker.signals.subtitle.connect(self.set_subtitle)
        worker.signals.estimated_time.connect(self.set_estimated_time)
        worker.signals.finished.connect(self.hide_progress_bar)

        self.thread_pool.start(worker)

    def on_run_alg_button_clicked(self):
        self.show_progress_bar()
        RunAlgorithm.run_alg()