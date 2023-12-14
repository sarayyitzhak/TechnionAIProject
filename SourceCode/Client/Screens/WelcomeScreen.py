from PyQt5.QtGui import QFont

from SourceCode.Client.Screens.Screen import *


class WelcomeScreen(Screen):
    def __init__(self, on_dev_clicked, on_prod_clicked):
        super().__init__()

        self.on_dev_clicked = on_dev_clicked
        self.on_prod_clicked = on_prod_clicked
        self.init_ui()

    def init_ui(self):
        label = QLabel("Welcome to our Amazing App")
        label.setFont(QFont('Arial', 24))
        self.layout.addWidget(label, 0, 0, 1, 1, Qt.AlignCenter)
        self.build_button("Development", self.on_dev_clicked, 1, 0, 1, 2)
        self.build_button("Production", self.on_prod_clicked, 2, 0, 1, 2)
