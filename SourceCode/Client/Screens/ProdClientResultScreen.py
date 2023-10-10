from SourceCode.Client.Screens.Screen import Screen
from PyQt5.QtGui import QFont

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap


class ProdClientResultScreen(Screen):
    def __init__(self, on_try_again_clicked):
        super().__init__()

        self.on_try_again_clicked = on_try_again_clicked
        self.rate_label = None
        self.pix_map_label = None

        self.init_ui()

    def init_ui(self):
        label = QLabel('The predicted rate of your restaurant is: ')
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        self.rate_label = QLabel()
        self.rate_label.setFont(QFont('Ariel', 30))
        self.rate_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.rate_label)

        self.pix_map_label = QLabel()
        self.layout.addWidget(self.pix_map_label, 2, 0, Qt.AlignCenter)

        try_again_button = self.build_button("Try Again", self.on_try_again_clicked, 3)
        try_again_button.setFixedSize(350, 70)

    def set_result(self, result):
        self.set_rate(result["prediction"].value)

    def set_rate(self, rate):
        self.rate_label.setText(str(rate))
        pix_map = QPixmap(self.choose_chef_image(rate))
        self.pix_map_label.setPixmap(pix_map.scaled(300, 300))

    @staticmethod
    def choose_chef_image(rate):
        if rate >= 80:
            return './Assets/happy_chef.png'
        elif rate >= 60:
            return './Assets/ok_chef.png'
        elif rate >= 40:
            return './Assets/eat_chef.png'
        elif rate >= 20:
            return './Assets/sad_chef.png'
        else:
            return './Assets/angry_chef.png'

