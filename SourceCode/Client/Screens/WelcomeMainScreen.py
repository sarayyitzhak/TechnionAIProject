from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QMessageBox, QGridLayout
from PyQt5.QtWidgets import *


class WelcomeMainScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.layout: QGridLayout = None
        self.dev_button: QPushButton = None
        self.prod_button: QPushButton = None
        self.init_ui()

    def init_ui(self):
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')
        # self.setWindowTitle("Restaurant Rating Predictor")

        self.layout = QGridLayout()
        self.build_buttons()

        self.layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(self.layout)

    def build_buttons(self):
        self.dev_button = self.build_button(0, 0, "Development")
        self.prod_button = self.build_button(1, 0, "Production")

    def build_button(self, i, j, label):
        button = QPushButton(label)
        self.layout.addWidget(button, i, j)
        return button


