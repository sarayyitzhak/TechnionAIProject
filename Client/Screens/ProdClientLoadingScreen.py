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

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        loading_gif = QMovie("./Client/Assets/loading.gif")
        label.setMovie(loading_gif)
        loading_gif.setScaledSize(QSize().scaled(200, 200, Qt.KeepAspectRatio))
        loading_gif.start()

        self.layout.addWidget(label)
        self.layout.setContentsMargins(200, 200, 200, 200)

        self.setLayout(self.layout)





