import time

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Server.DataBuilder import RestDataBuilder, CbsDataBuilder, GovDataBuilder, GoogleDataBuilder
from Server.DataParser import DataParser
from Server.Algo import RunAlgorithm


class ClientDev:
    def __init__(self):
        super().__init__()
        app = QApplication([])
        app.setStyle('Fusion')
        palette = QPalette()
        palette.setColor(QPalette.ButtonText, Qt.darkBlue)
        app.setStyleSheet("QPushButton { padding: 5ex; margin: 2ex;}")

        app.setPalette(palette)
        window = QWidget()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.completed = 0

        window.setWindowTitle("Regression tree Builder ")

        self.build_buttons()

        self.layout.setContentsMargins(50, 50, 50, 50)

        window.setLayout(self.layout)
        window.show()

        app.exec()

    def build_buttons(self):
        self.layout = QGridLayout()
        build_google_button = QPushButton("Build Google data")
        self.layout.addWidget(build_google_button, 0, 0)
        build_google_button.clicked.connect(self.on_build_google_button_clicked)

        build_rest_button = QPushButton("Build Rest data")
        self.layout.addWidget(build_rest_button, 0, 1)
        build_rest_button.clicked.connect(self.on_build_rest_button_clicked)

        build_cbs_button = QPushButton("Build CBS data")
        self.layout.addWidget(build_cbs_button, 0, 2)
        build_cbs_button.clicked.connect(self.on_build_cbs_button_clicked)

        build_gov_button = QPushButton("Build Gov data")
        self.layout.addWidget(build_gov_button, 0, 3)
        build_gov_button.clicked.connect(self.on_build_gov_button_clicked)

        build_all_button = QPushButton("Build all data")
        self.layout.addWidget(build_all_button, 1, 0, 1, 4)
        build_all_button.clicked.connect(self.on_build_all_button_clicked)

        parse_data_button = QPushButton("Parse data")
        self.layout.addWidget(parse_data_button, 2, 0, 1, 4)
        parse_data_button.clicked.connect(self.on_parse_data_button_clicked)

        run_alg_button = QPushButton("Run algorithm")
        self.layout.addWidget(run_alg_button, 3, 0, 1, 4)
        run_alg_button.clicked.connect(self.on_run_alg_button_clicked)

    def build_button(self, i, j, width, label, function):
        #TODO: use
        button = QPushButton(label)
        self.layout.addWidget(button, i, j, 1, width)
        button.clicked.connect(function)

    def build_progress_bar(self):
        self.label = QLabel("Parsing Data...")
        self.layout.addWidget(self.label, 4, 0, 1, 4)
        self.label.show()

        self.layout.addWidget(self.progress_bar, 5, 0, 1, 4)
        self.progress_bar.show()

        while self.completed < 100:
            self.completed += 0.00002
            self.progress_bar.setValue(int(self.completed))

            if self.progress_bar.value() == 100:
                time.sleep(1)
                self.progress_bar.hide()
                self.label.hide()

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
        self.build_progress_bar()
        DataParser.parse_data()

    def on_run_alg_button_clicked(self):
        self.build_progress_bar()
        RunAlgorithm.run_alg()


if __name__ == '__main__':
    # main()
    x = ClientDev()



