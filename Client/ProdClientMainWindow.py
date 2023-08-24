from Client.Screens.ProdClientMainScreen import *
from Client.Screens.ProdClientLoadingScreen import *
from Client.Screens.ProdClientResultScreen import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow

from Client.Workers.PredictionWorker import PredictionWorker


class ProdClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screens = QStackedWidget()

        self.main_window = ProdClientMainScreen()
        self.loading_window = ProdClientLoadingScreen()
        # self.results_window = ProdClientResultScreen(rate)
        self.results_window = ProdClientResultScreen()

        self.worker_thread = None
        self.worker = None

        self.main_window.calculate_button.clicked.connect(self.on_calc_button_clicked)
        self.results_window.try_again_button.clicked.connect(self.on_try_again_button_clicked)

        self.screens.addWidget(self.main_window)
        self.screens.addWidget(self.loading_window)
        self.screens.addWidget(self.results_window)

        self.screens.setWindowTitle("Restaurant Rating Predictor")

        self.screens.showMaximized()
        self.screens.show()

    def on_calc_button_clicked(self):
        self.create_worker()
        self.screens.setCurrentWidget(self.loading_window)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

    def calc_finished(self):
        self.worker_thread.quit()
        self.screens.setCurrentWidget(self.results_window)

    def on_try_again_button_clicked(self):
        self.screens.setCurrentWidget(self.main_window)

    def create_worker(self):
        self.worker_thread = QThread()
        self.worker = PredictionWorker()
        self.worker_thread.started.connect(self.worker.run_alg)
        self.worker.finished.connect(self.calc_finished)
