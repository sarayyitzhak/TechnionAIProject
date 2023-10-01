from SourceCode.Client.Screens.Screen import Screen
from SourceCode.Client.Workers.Worker import *
from PyQt5.QtGui import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class ProdClientLoadingScreen(Screen):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.run_gif()

    def init_ui(self):
        loading_label = QLabel("Loading...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setFont(QFont('Arial', 26))
        self.layout.addWidget(loading_label)

    def run_gif(self):
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        loading_gif = QMovie("./Assets/loading.gif")
        label.setMovie(loading_gif)
        loading_gif.setScaledSize(QSize().scaled(200, 200, Qt.KeepAspectRatio))
        loading_gif.start()
        self.layout.addWidget(label)



