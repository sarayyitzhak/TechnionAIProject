from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Server.Algo import RunAlgorithm
from Client.DataParserWorker import *
from Client.GoogleDataBuilderWorker import *
from Client.RestDataBuilderWorker import *
from Client.CbsDataBuilderWorker import *
from Client.GovDataBuilderWorker import *


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
        self.on_button_clicked(GoogleDataBuilderWorker('./DataConfig/google-data-config.json'))

    def on_build_rest_button_clicked(self):
        self.on_button_clicked(RestDataBuilderWorker('./DataConfig/rest-data-config.json'))

    def on_build_cbs_button_clicked(self):
        self.on_button_clicked(CbsDataBuilderWorker('./DataConfig/cbs-data-config.json'))

    def on_build_gov_button_clicked(self):
        self.on_button_clicked(GovDataBuilderWorker('./DataConfig/gov-data-config.json'))

    def on_build_all_button_clicked(self):
        self.on_build_google_button_clicked()
        self.on_build_rest_button_clicked()
        self.on_build_cbs_button_clicked()
        self.on_build_gov_button_clicked()

    def on_parse_data_button_clicked(self):
        self.on_button_clicked(DataParserWorker('./DataConfig/data-parser-config.json'))

    def on_run_alg_button_clicked(self):
        RunAlgorithm.run_alg()

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
