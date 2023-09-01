from Client.Screens.ProdClientMainScreen import *
from Client.Screens.ProdClientLoadingScreen import *
from Client.Screens.ProdClientResultScreen import *
from Client.Screens.DevClientMainScreen import *
from Client.Screens.WelcomeMainScreen import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow
from Client.Workers.PredictionWorker import PredictionWorker


class ProdClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screens = QStackedWidget()
        self.prod_main_screen = ProdClientMainScreen()
        self.prod_loading_screen = ProdClientLoadingScreen()
        self.prod_results_screen = ProdClientResultScreen()
        self.dev_main_screen = DevClientMainScreen()
        self.main_screen = WelcomeMainScreen()
        self.prediction_worker_thread = None
        self.prediction_worker = None
        self.init_stack()
        self.on_buttons_click()

        self.screens.setWindowTitle("Restaurant Rating Predictor")

        self.screens.showMaximized()
        self.screens.show()

    def init_stack(self):
        self.screens.addWidget(self.main_screen)
        self.screens.addWidget(self.prod_main_screen)
        self.screens.addWidget(self.prod_loading_screen)
        self.screens.addWidget(self.prod_results_screen)
        self.screens.addWidget(self.dev_main_screen)

    def on_buttons_click(self):
        self.main_screen.prod_button.clicked.connect(self.on_build_prod_button_clicked)
        self.main_screen.dev_button.clicked.connect(self.on_build_dev_button_clicked)
        self.prod_main_screen.calculate_button.clicked.connect(self.on_calc_button_clicked)
        self.prod_results_screen.try_again_button.clicked.connect(self.on_try_again_button_clicked)
        self.dev_main_screen.return_button.clicked.connect(self.on_return_button_clicked)
        self.prod_main_screen.return_button.clicked.connect(self.on_return_button_clicked)

    def on_calc_button_clicked(self):
        # loading_thread = QThread()
        # loading_worker = PredictionWorker(self.main_window.res)
        # loading_thread.started.connect(self.loading_window.run_gif())
        # loading_worker.moveToThread(loading_worker)
        # loading_thread.start()


        self.screens.setCurrentWidget(self.prod_loading_screen)
        QCoreApplication.processEvents()
        self.create_worker()
        self.prediction_worker.moveToThread(self.prediction_worker_thread)
        self.prediction_worker_thread.start()

    def calc_finished(self, rate):
        self.prod_results_screen.set_rate(rate)
        self.prediction_worker_thread.quit()
        self.screens.setCurrentWidget(self.prod_results_screen)

    def on_try_again_button_clicked(self):
        self.screens.setCurrentWidget(self.prod_main_screen)

    def create_worker(self):
        self.prediction_worker_thread = QThread()
        self.prediction_worker = PredictionWorker(self.prod_main_screen.res)
        self.prediction_worker_thread.started.connect(self.prediction_worker.run_alg)
        self.prediction_worker.finished.connect(self.calc_finished)

    def on_build_dev_button_clicked(self):
        self.screens.setCurrentWidget(self.dev_main_screen)

    def on_build_prod_button_clicked(self):
        self.screens.setCurrentWidget(self.prod_main_screen)

    def on_return_button_clicked(self):
        self.screens.setCurrentWidget(self.main_screen)
