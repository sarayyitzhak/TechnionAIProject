from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap


def choose_chef_image(rate):
    if float(rate) >= 80:
        return './Client/Assets/happy_chef.png'
    elif float(rate) >= 60:
        return './Client/Assets/ok_chef.png'
    elif float(rate) >= 40:
        return './Client/Assets/eat_chef.png'
    elif float(rate) >= 20:
        return './Client/Assets/sad_chef.png'
    else:
        return './Client/Assets/angry_chef.png'


class ProdClientResultScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyle(QStyleFactory.create("Fusion"))

        self.layout = QGridLayout()
        self.setStyleSheet("QLabel{font-size: 26pt;}")

        label = QLabel('The predicted rate of your restaurant is: ')
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        rate = '0'
        rate_label = QLabel(str(rate))
        rate_label.setFont(QFont('Ariel', 30))
        rate_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(rate_label)

        self.pixmap_label = QLabel(self)

        self.pixmap = QPixmap(choose_chef_image(rate))
        scaled_pixmap = self.pixmap.scaled(300, 300)
        self.pixmap_label.setPixmap(scaled_pixmap)
        self.layout.addWidget(self.pixmap_label, 2, 0, Qt.AlignCenter)

        self.try_again_button = QPushButton("Try Again")
        self.try_again_button.setFixedSize(350, 70)
        self.layout.addWidget(self.try_again_button, 3, 0, Qt.AlignCenter)

        self.layout.setContentsMargins(200, 200, 200, 200)

        self.setLayout(self.layout)
