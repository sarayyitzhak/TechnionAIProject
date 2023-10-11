from SourceCode.Client.Screens.Screen import Screen
from PyQt5.QtGui import QFont

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from SourceCode.Common.FileUtils import *
from SourceCode.Server.Utils.Time import Time


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
        self.set_user_selection(result["user_selection"])

    def clear_all_widgets(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def set_rate(self, prediction):
        self.add_label(0, "The predicted rate of your restaurant is:", 12, True)
        self.add_label(1, str(round(prediction.value, 2)), 30)
        self.add_image(2, self.get_chef_image_path(prediction.value))
        self.add_label(3, f"Found approximately {prediction.size} restaurants like yours")
        self.add_label(4, f"Rating accuracy: {round(1 - prediction.mae, 2) * 100}%")

    def set_user_selection(self, user_selection):
        first_row_fields = [field for field in self.config["fields"] if field["type"] == "FIRST_ROW"]
        bool_fields = [field for field in self.config["fields"] if field["type"] == "BOOL"]
        activity_hours_fields = [field for field in self.config["fields"] if field["type"] == "ACTIVITY_HOURS"]
        number_fields = [field for field in self.config["fields"] if field["type"] == "NUMBER"]

        self.add_label(5, "User Selection and values filled by the system:", 12, True)

        row_index = self.layout.rowCount()

        for idx, field in enumerate(first_row_fields):
            label = self.get_user_selection_label(field, str(user_selection[field['name']]))
            self.layout.addWidget(label, row_index + int(idx / 5), idx % 5)

        row_index = self.layout.rowCount()

        for idx, field in enumerate(bool_fields):
            label = self.get_user_selection_label(field, str(user_selection[field['name']]))
            self.layout.addWidget(label, row_index + int(idx / 5), idx % 5)

        row_index = self.layout.rowCount()

        for field in activity_hours_fields:
            from_time = Time(total_minutes=user_selection[field['from_name']])
            to_time = Time(total_minutes=user_selection[field['to_name']])
            label = self.get_user_selection_label(field, f"{str(from_time)} - {str(to_time)}")
            self.layout.addWidget(label, row_index, 0, 1, 1)
            row_index += 1

        row_index = self.layout.rowCount() - len(activity_hours_fields)

        for field in number_fields:
            label = self.get_user_selection_label(field, str(user_selection[field['name']]))
            self.layout.addWidget(label, row_index, 1, 1, 1)
            row_index += 1

        row_index = self.layout.rowCount() - len(number_fields)

        try_again_row_span = max(len(activity_hours_fields), len(number_fields))
        try_again_button = self.build_button("Try Again", self.on_try_again_clicked, row_index, 2, 3, try_again_row_span, True)
        try_again_button.setFixedSize(350, 70)

    def add_label(self, row, text, font_size=None, bold=False):
        label = QLabel(text)
        if font_size is not None:
            label.setFont(QFont('Arial', font_size))
        if bold:
            label.setStyleSheet("font-weight: bold")
        self.layout.addWidget(label, row, 0, 1, 5, Qt.AlignCenter)

    def add_image(self, row, image_path):
        pix_map = QPixmap(image_path)
        pix_map_label = QLabel()
        pix_map_label.setPixmap(pix_map.scaled(200, 200))
        self.layout.addWidget(pix_map_label, row, 0, 1, 5, Qt.AlignCenter)

    @staticmethod
    def get_user_selection_label(field, value):
        label = QLabel(f"{field['string']}: <b>{value}</b>")
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

