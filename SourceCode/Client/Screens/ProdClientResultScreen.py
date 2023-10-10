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

    def set_result(self, result):
        user_selection = result["user_selection"]
        self.set_rate(result["prediction"].value)

        first_row_fields = [field for field in self.config["fields"] if field["type"] == "FIRST_ROW"]
        bool_fields = [field for field in self.config["fields"] if field["type"] == "BOOL"]
        activity_hours_fields = [field for field in self.config["fields"] if field["type"] == "ACTIVITY_HOURS"]
        number_fields = [field for field in self.config["fields"] if field["type"] == "NUMBER"]

        label = QLabel("User Selection and values filled by the system:")
        label.setFont(QFont('Arial', 12))
        label.setStyleSheet("font-weight: bold")
        self.layout.addWidget(label, self.layout.rowCount(), 0, 1, 5)

        row_index = self.layout.rowCount()

        for idx, field in enumerate(first_row_fields):
            self.layout.addWidget(self.get_label(field, str(user_selection[field['name']])), row_index + int(idx / 5), idx % 5)

        row_index = self.layout.rowCount()

        for idx, field in enumerate(bool_fields):
            self.layout.addWidget(self.get_label(field, str(user_selection[field['name']])), row_index + int(idx / 5), idx % 5)

        row_index = self.layout.rowCount()

        for field in activity_hours_fields:
            from_time = Time(total_minutes=user_selection[field['from_name']])
            to_time = Time(total_minutes=user_selection[field['to_name']])
            self.layout.addWidget(self.get_label(field, f"{str(from_time)} - {str(to_time)}"), row_index, 0, 1, 1)
            row_index += 1

        row_index = self.layout.rowCount() - len(activity_hours_fields)

        for field in number_fields:
            self.layout.addWidget(self.get_label(field, str(user_selection[field['name']])), row_index, 1, 1, 1)
            row_index += 1

        row_index = self.layout.rowCount() - len(number_fields)

        try_again_row_span = max(len(activity_hours_fields), len(number_fields))
        try_again_button = self.build_button("Try Again", self.on_try_again_clicked, row_index, 2, 3, try_again_row_span, True)
        try_again_button.setFixedSize(350, 70)

    @staticmethod
    def get_label(field, value):
        label = QLabel(f"{field['string']}: <b>{value}</b>")
        label.setTextFormat(Qt.RichText)
        return label

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

