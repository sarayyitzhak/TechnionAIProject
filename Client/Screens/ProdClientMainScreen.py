import io
import json
import folium
from PyQt5.QtCore import QTime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Server.DataFiller import *
from Client.Screens.ProdClientResultScreen import *
from PyQt5.QtWidgets import *


class ProdClientMainScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')

        try:
            with open('./ConfigFiles/prod-config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except IOError:
            print("Error")

        self.res = {}
        self.loading_screen = None
        self.result_screen = None
        self.check_box_group = None
        self.check_box_layout = None
        self.combo_box_group = None
        self.combo_box_layout = None
        self.address_group = None
        self.address_layout = None
        self.address_text_box = None
        self.web_view = None
        self.final_res = None
        self.activity_hours_group = None
        self.activity_hours_layout = None
        self.res_activity_hours = None
        self.res_bool = None
        self.res_multi_choice = None
        self.res_location = None
        self.coor_layout = None
        self.city_text_box = None
        self.street_text_box = None
        self.geo_loc_text_box = None
        self.data_filler = None

        self.data_fields = [field for field in self.config["fields"]]
        self.bool_fields = [field for field in self.config["fields"] if field["type"] == "BOOL"]
        self.selection_fields = [field for field in self.data_fields if field["type"] == "SELECTION"]
        self.location_fields = [field for field in self.data_fields if field["type"] == "LOCATION"]
        self.activity_fields = [field for field in self.data_fields if field["type"] == "ACTIVITY_HOURS"]
        self.location = (self.config["default_location"]["lat"], self.config["default_location"]["lng"])

        self.init_selection()

        self.layout = QGridLayout()
        self.build_widgets()

        self.calculate_button = self.build_button(4, 0, "Calculate", self.on_calculate_button_clicked, self.layout)

        self.add_layouts()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(100, 100, 100, 100)

    def init_selection(self):
        open_total_minutes = Time(hours=8, minutes=0).get_total_minutes()
        close_total_minutes = Time(hours=23, minutes=0).get_total_minutes()
        self.res_activity_hours = [open_total_minutes, close_total_minutes] * 14
        self.res_bool = {field["name"]: False for field in self.bool_fields}
        self.res_multi_choice = {field["name"]: None for field in self.selection_fields}
        self.res_location = {field["name"]: None for field in self.location_fields}

    def on_calculate_button_clicked(self):
        self.update_location_data()
        self.set_info()
        self.final_res = [self.res[field["name"]] for field in self.data_fields if field["name"] in self.res]

    def set_info(self):
        self.res.update(self.res_bool)
        self.res.update(self.res_multi_choice)
        self.res.update(self.res_location)
        self.res.update(self.res_calc_features_by_activity())
        self.res.update(self.res_calc_features_by_loc())

    def res_calc_features_by_activity(self):
        data = {}
        activity_hours = []
        for day in range(7):
            activity_hours.append([self.res_activity_hours[day * 2], self.res_activity_hours[(day * 2) + 1]])

        for idx, day in enumerate(self.activity_fields):
            data[day["name"]] = activity_hours[idx]
        for is_open, mean in enumerate([field for field in self.data_fields if field["type"] == "MEAN"]):
            data[mean["name"]] = ActivityTimeFiller.get_mean_activity_hour(activity_hours, 1 - is_open)
        saturday = [field for field in self.data_fields if field["type"] == "SATURDAY"].pop()
        data[saturday["name"]] = ActivityTimeFiller.is_open_on_saturday(activity_hours)
        return data

    def res_calc_features_by_loc(self):
        data = {}
        config_file = open('./ConfigFiles/data-parser-config.json', 'r', encoding='utf-8')
        self.data_filler = DataFiller(json.load(config_file))
        self.data_filler.get_places_data()
        data.update(self.data_filler.get_places_data_by_point(tuple(self.res_location["geo_location"]), None))
        self.data_filler.get_cbs_data()
        data.update(self.data_filler.get_cbs_data_by_address(self.res_location["city"], self.res_location["street"]))
        return data

    def update_location_data(self):
        self.res_location["city"] = self.city_text_box.text()
        self.res_location["street"] = self.street_text_box.text()
        self.res_location["geo_location"] = [float(s) for s in self.geo_loc_text_box.text().split() if s.replace('.', '', 1).isdigit()]

    def build_widgets(self):
        self.create_check_box_group()
        self.create_combo_box_group()
        self.create_address_group()
        self.create_activity_hours_group()

    def add_layouts(self):
        self.layout.addLayout(self.check_box_layout, 0, 0)
        self.layout.addLayout(self.combo_box_layout, 1, 0)
        self.layout.addLayout(self.address_layout, 2, 0)
        self.layout.addLayout(self.activity_hours_layout, 3, 0)

    def create_activity_hours_group(self):
        self.activity_hours_group = QGroupBox()
        self.activity_hours_layout = QGridLayout()
        self.activity_hours_layout.setSpacing(10)
        days = self.config["days"]
        for idx, day in enumerate(days):
            self.create_activity_hours_per_day(idx, days[idx])

    def create_activity_hours_per_day(self, day, label_day):
        self.create_activity_hours_labels(day, label_day)
        self.create_activity_widget(day, True)
        self.create_activity_widget(day, False)

    def create_activity_widget(self, day, is_opening):
        activity_time = QTimeEdit(self)
        default = QTime(23, 0)
        row = 4
        if is_opening:
            default = QTime(8, 0)
            row = 2
        activity_time.setTime(default)
        activity_time.editingFinished.connect(lambda: self.update_activity_hours(activity_time, day, is_opening))
        self.activity_hours_layout.addWidget(activity_time, row, day)

    def create_activity_hours_labels(self, day, label_day):
        full_label = "Enter " + label_day + " activity"
        self.create_text_label(full_label, self.activity_hours_layout, 0, day)
        self.create_text_label("from:", self.activity_hours_layout, 1, day)
        self.create_text_label("to:", self.activity_hours_layout, 3, day)

    def create_address_group(self):
        self.address_group = QGroupBox()
        self.address_layout = QGridLayout()
        self.create_address_text_boxes()
        self.create_map()
        self.address_layout.addLayout(self.coor_layout, 0, 0)

    def create_map(self):
        gmap = folium.Map(zoom_start=11, location=self.location)
        data = io.BytesIO()
        gmap.add_child(folium.LatLngPopup())
        gmap.save(data, close_file=False)

        self.web_view = QWebEngineView()
        self.web_view.setHtml(data.getvalue().decode())
        self.address_layout.addWidget(self.web_view, 0, 1)

    def create_address_text_boxes(self):
        self.coor_layout = QGridLayout()
        self.coor_layout.setContentsMargins(0, 50, 50, 50)
        self.create_text_label("Please enter your city and street below", self.coor_layout, 0, 0)
        self.city_text_box = self.create_address_text_box("Enter city", 1, 0)
        self.street_text_box = self.create_address_text_box("Enter street", 1, 1)
        self.create_text_label("Then find your coordinates in the map and enter them below", self.coor_layout, 2, 0)
        self.geo_loc_text_box = self.create_address_text_box("Enter coordinates", 3, 0, 2)

    def create_address_text_box(self, text, i, j, width=1):
        text_box = QLineEdit(self)
        text_box.setPlaceholderText(text)
        self.coor_layout.addWidget(text_box, i, j, 1, width)
        return text_box

    def create_check_box_group(self):
        self.check_box_group = QGroupBox()
        self.check_box_layout = QGridLayout()

        for idx, field in enumerate([field for field in self.bool_fields]):
            self.create_check_box(field, int(idx / 3), idx % 3)

    def create_combo_box_group(self):
        self.combo_box_group = QGroupBox()
        self.combo_box_layout = QGridLayout()
        self.combo_box_layout.setSpacing(100)
        try:
            with open('./ConfigFiles/prod-data-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                for idx, field in enumerate([field for field in self.selection_fields]):
                    self.create_combo_box(config, field, 0, idx)
        except IOError:
            print("Error")

    def create_combo_box(self, config, field, i, j):
        combo_box = QComboBox(self)
        combo_box.addItem(field["string"])
        combo_box.addItems(config[field["name"]])
        combo_box.currentTextChanged.connect(lambda: self.on_combo_box_changed(field, combo_box))
        self.combo_box_layout.addWidget(combo_box, i, j)

    def on_combo_box_changed(self, field, combo_box):
        self.res_multi_choice[field["name"]] = combo_box.currentText()

    def create_check_box(self, field, i, j):
        checkbox = QCheckBox(field["string"])
        self.check_box_layout.addWidget(checkbox, i, j)
        checkbox.stateChanged.connect(lambda: self.on_check_box_clicked(field))

    def on_check_box_clicked(self, field):
        self.res_bool[field["name"]] = not self.res_bool[field["name"]]

    @staticmethod
    def build_button(i, j, label, function, layout, width=1):
        button = QPushButton(label)
        button.clicked.connect(function)
        layout.addWidget(button, i, j, 1, width)
        return button

    def update_activity_hours(self, activity_time, day, is_opening):
        value = activity_time.time().toPyTime()
        idx = 0 if is_opening else 1
        self.res_activity_hours[2 * day + idx] = Time(hours=value.hour, minutes=value.minute).get_total_minutes()

    @staticmethod
    def create_text_label(text, layout, i, j):
        label = QLabel(text)
        layout.addWidget(label, i, j)

