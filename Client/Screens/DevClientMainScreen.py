from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from Client.Workers.DataParserWorker import *
from Client.Workers.GoogleDataBuilderWorker import *
from Client.Workers.RestDataBuilderWorker import *
from Client.Workers.CbsDataBuilderWorker import *
from Client.Workers.GovDataBuilderWorker import *
from Client.Workers.RunAlgorithmWorker import *
from Client.Workers.Worker import *
from Server.DataBuilder.Utils import write_to_file

import pandas as pd



class DevClientMainWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.layout: QGridLayout = None
        self.scroll: QScrollArea = None
        self.scroll_layout: QVBoxLayout = None

        self.thread_pool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')
        self.setWindowTitle("Restaurant Rating Predictor")

        self.layout = QGridLayout()
        self.build_buttons()
        self.build_scroll_bar()

        self.layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(self.layout)

    def build_buttons(self):
        self.build_button(0, 0, 1, "Build Google Data", self.on_build_google_button_clicked)
        self.build_button(0, 1, 1, "Build Rest Data", self.on_build_rest_button_clicked)
        self.build_button(0, 2, 1, "Build CBS Data", self.on_build_cbs_button_clicked)
        self.build_button(0, 3, 1, "Build Gov Data", self.on_build_gov_button_clicked)
        self.build_button(1, 0, 4, "Build All Data", self.on_build_all_button_clicked)
        self.build_button(2, 0, 4, "Get Data Config", self.on_data_config_button_clicked)
        self.build_button(3, 0, 4, "Parse Data", self.on_parse_data_button_clicked)
        self.build_button(4, 0, 4, "Run Algorithm", self.on_run_alg_button_clicked)

    def build_button(self, i, j, width, label, function):
        button = QPushButton(label)
        self.layout.addWidget(button, i, j, 1, width)
        button.clicked.connect(function)

    def build_scroll_bar(self):
        self.scroll = QScrollArea()
        widget = QWidget()
        self.scroll_layout = QVBoxLayout(widget)
        self.scroll.setWidget(widget)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(150)

        self.layout.addWidget(self.scroll, 4, 0, 1, 4)
        self.scroll.hide()

    def on_build_google_button_clicked(self):
        self.on_button_clicked(GoogleDataBuilderWorker('./ConfigFiles/google-data-config.json'))

    def on_build_rest_button_clicked(self):
        self.on_button_clicked(RestDataBuilderWorker('./ConfigFiles/rest-data-config.json'))

    def on_build_cbs_button_clicked(self):
        self.on_button_clicked(CbsDataBuilderWorker('./ConfigFiles/cbs-data-config.json'))

    def on_build_gov_button_clicked(self):
        self.on_button_clicked(GovDataBuilderWorker('./ConfigFiles/gov-data-config.json'))

    def on_build_all_button_clicked(self):
        self.on_build_google_button_clicked()
        self.on_build_rest_button_clicked()
        self.on_build_cbs_button_clicked()
        self.on_build_gov_button_clicked()

    @staticmethod
    def on_data_config_button_clicked():
        try:
            data = pd.read_csv("./Server/Dataset/data.csv")
            price_level_as_num = data["price_level"].dropna().unique()
            price_level_as_num.sort()
            types = data["type"].dropna().unique().tolist()
            types.remove("כשר") #TODO: Remove
            config = {
                "type": types,
                "price_level": ['$' * int(num) for num in price_level_as_num]
                }
            write_to_file(config, "./ConfigFiles/prod-data-config.json")
        except IOError:
            print("Error")

    # @staticmethod
    def on_parse_data_button_clicked(self):
        self.on_button_clicked(DataParserWorker('./ConfigFiles/data-parser-config.json'))

    def on_run_alg_button_clicked(self):
        self.on_button_clicked(RunAlgorithmWorker('./ConfigFiles/algo-config.json'))

    def on_button_clicked(self, worker):
        group_box = QGroupBox()
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        title = QLabel()
        subtitle = QLabel()
        estimated_time = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(progress_bar)
        layout.addWidget(estimated_time)
        group_box.setLayout(layout)

        self.scroll_layout.addWidget(group_box)
        self.scroll.show()

        worker.signals.progress.connect(progress_bar.setValue)
        worker.signals.title.connect(title.setText)
        worker.signals.subtitle.connect(subtitle.setText)
        worker.signals.estimated_time.connect(estimated_time.setText)
        worker.signals.error.connect(self.show_error_message_box)
        worker.signals.finished.connect(lambda: self.on_worker_finished(group_box))

        self.thread_pool.start(worker)

    def on_worker_finished(self, widget):
        self.scroll_layout.removeWidget(widget)
        if self.thread_pool.activeThreadCount() == 0:
            self.scroll.hide()

    @staticmethod
    def show_error_message_box(value):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"{value[1]}\n\n{value[2]}")
        msg.setWindowTitle(value[0])
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
