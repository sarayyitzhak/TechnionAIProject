from Client.Screens.ProdClientLoadingScreen import *
from Server.Algo.ID3Experiments import *
import time
from PyQt5.QtCore import pyqtSignal, QObject


class PredictionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run_alg(self):
        # TODO: run the prediction algorithem
        try:
            with open('./DataOutput/algo-tree.json', 'r', encoding='utf-8') as f:
                self.formatted_tree = json.load(f)
        except IOError:
            print("Error")

        # pred = Prediction()
        # pred.create_decision_tree(self.formatted_tree)
        # pred.predict_sample(self.customer_choise, False) #TODO: should be mainwindow.res


        for i in range(1, 21):
            time.sleep(0.1)  # Simulate some work
            self.progress.emit(i)
            QCoreApplication.processEvents()
        self.finished.emit()