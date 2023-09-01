from PyQt5 import QtWidgets, QtGui, QtCore
from Client.Workers.Worker import *
from PyQt5.QtGui import QMovie

from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class ProdClientLoadingScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.setStyleSheet("QLabel{font-size: 26pt;}")
        loading_label = QLabel("Loading...")
        loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(loading_label)
        self.run_gif()

        self.layout.setContentsMargins(200, 200, 200, 200)

        self.setLayout(self.layout)

    def run_gif(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.loading_gif = QMovie("./Client/Assets/loading.gif")
        self.label.setMovie(self.loading_gif)
        self.loading_gif.setScaledSize(QSize().scaled(200, 200, Qt.KeepAspectRatio))
        self.loading_gif.start()
        self.layout.addWidget(self.label)



