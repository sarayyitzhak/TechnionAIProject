from SourceCode.Client.Screens.Screen import Screen
from PyQt5.QtGui import QFont

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from SourceCode.Common.FileUtils import *


class ProdClientResultScreen(Screen):
    def __init__(self, on_try_again_clicked):
        super().__init__()

        self.on_try_again_clicked = on_try_again_clicked

        self.config = None
        self.rate_label = None
        self.pix_map_label = None

        read_from_file('./ConfigFiles/prod-results-config.json', self.on_config_file_read, self.show_error_message_box)

    def on_config_file_read(self, config):
        self.config = config

    def set_result(self, result):
        self.clear_all_widgets()
        self.set_rate(result["prediction"])
        if result["find_best_rest_type"]:
            self.set_best_rest_type(result["user_selection"])
        self.set_nearby_info(result["user_selection"], result["same_type_count"], result["rest_count"], result["rest_pos"])

    def clear_all_widgets(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def set_rate(self, prediction):
        self.add_label(0, "<b>The predicted rate of your restaurant is:</b>", 12)
        self.add_label(1, str(round(prediction.value, 2)), 30)
        self.add_image(2, self.get_chef_image_path(prediction.value))
        self.add_label(3, f"Rating accuracy: <b>{round(1 - prediction.mae, 2) * 100}%</b>")

    def set_best_rest_type(self, user_selection):
        self.add_label(4, f"The best type of restaurant the system found: <b>{user_selection['type']}</b>")

    def set_nearby_info(self, user_selection, same_type_count, rest_count, rest_pos):
        row_index = self.layout.rowCount()

        self.add_label(row_index, "<b>More information nearby:</b>", 12)
        self.add_label(row_index + 1, f"Found approximately <b>{same_type_count}</b> restaurants like yours")
        self.add_label(row_index + 2, f"Position of your restaurant: <b>{rest_pos}/{rest_count}</b>")

        row_index += 3

        for idx, field in enumerate([field for field in self.config["fields"] if field["type"] == "NUMBER"]):
            label = self.get_user_selection_label(field['string'], str(user_selection[field['name']]))
            self.layout.addWidget(label, row_index + idx % 2, int(idx / 2), 1, 1)

        row_index = self.layout.rowCount()

        try_again_button = self.build_button("Try Again", self.on_try_again_clicked, row_index, 0, 4, 1, True)
        try_again_button.setFixedSize(350, 70)

    def add_label(self, row, text, font_size=None):
        label = QLabel(text)
        if font_size is not None:
            label.setFont(QFont('Arial', font_size))
        label.setTextFormat(Qt.RichText)
        self.layout.addWidget(label, row, 0, 1, 4, Qt.AlignCenter)

    def add_image(self, row, image_path):
        pix_map = QPixmap(image_path)
        pix_map_label = QLabel()
        pix_map_label.setPixmap(pix_map.scaled(200, 200))
        self.layout.addWidget(pix_map_label, row, 0, 1, 4, Qt.AlignCenter)

    @staticmethod
    def get_user_selection_label(title, value):
        label = QLabel(f"{title}: <b>{value}</b>")
        label.setTextFormat(Qt.RichText)
        return label

    @staticmethod
    def get_chef_image_path(rate):
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

