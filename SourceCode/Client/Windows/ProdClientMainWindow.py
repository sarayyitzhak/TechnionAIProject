from SourceCode.Client.Screens.ProdClientMainScreen import *
from SourceCode.Client.Screens.ProdClientLoadingScreen import *
from SourceCode.Client.Screens.ProdClientResultScreen import *
from SourceCode.Client.Screens.DevClientMainScreen import *
from SourceCode.Client.Screens.WelcomeScreen import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from SourceCode.Client.Workers.RunPredicitionWorker import RunPredictionWorker


class ProdClientMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.screens = QStackedWidget()
        self.prod_main_screen = ProdClientMainScreen(self.on_calc_clicked, self.change_to_welcome_screen)
        self.prod_loading_screen = ProdClientLoadingScreen()
        self.prod_results_screen = ProdClientResultScreen(self.change_to_prod_main_screen)
        self.dev_main_screen = DevClientMainScreen(self.change_to_welcome_screen)
        self.welcome_screen = WelcomeScreen(self.change_to_dev_main_screen, self.change_to_prod_main_screen)
        self.thread_pool = QThreadPool()
        self.init_stack()

        self.screens.setWindowTitle("Restaurant Rating Predictor")
        self.screens.setWindowIcon(QtGui.QIcon('./Assets/chef-hat.png'))

        self.screens.showMaximized()
        self.screens.show()

    def init_stack(self):
        self.screens.addWidget(self.welcome_screen)
        self.screens.addWidget(self.prod_main_screen)
        self.screens.addWidget(self.prod_loading_screen)
        self.screens.addWidget(self.prod_results_screen)
        self.screens.addWidget(self.dev_main_screen)

    def on_calc_clicked(self):
        self.screens.setCurrentWidget(self.prod_loading_screen)
        QCoreApplication.processEvents()
        user_selection = self.prod_main_screen.res
        rest_types = self.prod_main_screen.data_config["type"]
        run_prediction_worker = RunPredictionWorker("./ConfigFiles/prediction-config.json", user_selection, rest_types)
        run_prediction_worker.signals.finished.connect(self.on_prediction_finished)
        self.thread_pool.start(run_prediction_worker)

    def on_prediction_finished(self, result):
        self.prod_results_screen.set_result(result)
        self.screens.setCurrentWidget(self.prod_results_screen)

    def change_to_prod_main_screen(self):
        self.screens.setCurrentWidget(self.prod_main_screen)

    def change_to_dev_main_screen(self):
        self.screens.setCurrentWidget(self.dev_main_screen)

    def change_to_welcome_screen(self):
        self.screens.setCurrentWidget(self.welcome_screen)
