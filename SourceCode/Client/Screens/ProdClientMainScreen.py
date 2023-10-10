import io
import folium
from PyQt5.QtCore import QTime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from SourceCode.Client.Screens.Screen import Screen
from PyQt5.QtWidgets import *
from SourceCode.Common.FileUtils import *

from SourceCode.Server.Utils.Time import Time


class ProdClientMainScreen(Screen):
    def __init__(self, on_calc_clicked, on_return_clicked):
        super().__init__()

        self.on_calc_clicked = on_calc_clicked
        self.on_return_clicked = on_return_clicked

        self.config = None
        self.data_config = None
        self.res = {}

        self.res_activity = None
        self.res_bool = None
        self.res_multi_choice = None
        self.res_location = None

        self.city_text_box = None
        self.street_text_box = None
        self.geo_loc_text_box = None

        self.data_fields = None
        self.bool_fields = None
        self.selection_fields = None
        self.location_fields = None
        self.open_fields = None
        self.close_fields = None
        read_from_file('./ConfigFiles/prod-config.json', self.on_config_file_read, self.show_error_message_box)

    def on_config_file_read(self, config):
        self.config = config

        self.data_fields = [field for field in self.config["fields"]]
        self.bool_fields = [field for field in self.config["fields"] if field["type"] == "BOOL"]
        self.selection_fields = [field for field in self.data_fields if field["type"] == "SELECTION"]
        self.location_fields = [field for field in self.data_fields if field["type"] == "LOCATION"]
        self.open_fields = [field for field in self.data_fields if field["type"] == "OPEN"]
        self.close_fields = [field for field in self.data_fields if field["type"] == "CLOSE"]

        read_from_file('./ConfigFiles/prod-data-config.json', self.on_data_config_file_read, self.show_error_message_box)

    def on_data_config_file_read(self, data_config):
        self.data_config = data_config

        self.init_selection()

        self.build_layouts()
        self.build_buttons()

    def init_selection(self):
        open_total_minutes = Time(hours=8, minutes=0).get_total_minutes()
        close_total_minutes = Time(hours=23, minutes=0).get_total_minutes()
        self.res_activity = {field["name"]: open_total_minutes for field in self.open_fields}
        self.res_activity.update({field["name"]: close_total_minutes for field in self.close_fields})
        self.res_bool = {field["name"]: False for field in self.bool_fields}
        self.res_multi_choice = {field["name"]: None for field in self.selection_fields}
        self.res_location = {field["name"]: None for field in self.location_fields}

    def build_layouts(self):
        self.layout.addLayout(self.create_check_box_layout(), 0, 0)
        self.layout.addLayout(self.create_combo_box_layout(), 1, 0)
        self.layout.addLayout(self.create_address_layout(), 2, 0)
        self.layout.addLayout(self.create_activity_hours_layout(), 3, 0)

    def create_check_box_layout(self):
        check_box_layout = QGridLayout()

        for idx, field in enumerate([field for field in self.bool_fields]):
            self.create_check_box(check_box_layout, field, int(idx / 3), idx % 3)

        return check_box_layout

    def create_check_box(self, check_box_layout, field, i, j):
        checkbox = QCheckBox(field["string"])
        check_box_layout.addWidget(checkbox, i, j)
        checkbox.stateChanged.connect(lambda: self.on_check_box_clicked(field))

    def on_check_box_clicked(self, field):
        self.res_bool[field["name"]] = not self.res_bool[field["name"]]

    def create_combo_box_layout(self):
        combo_box_layout = QGridLayout()
        combo_box_layout.setSpacing(100)

        for idx, field in enumerate([field for field in self.selection_fields]):
            self.create_combo_box(combo_box_layout, field, idx)

        return combo_box_layout

    def create_combo_box(self, combo_box_layout, field, j):
        combo_box = QComboBox(self)
        combo_box.addItem(field["string"])
        combo_box.addItems(self.data_config[field["name"]])
        combo_box.currentTextChanged.connect(lambda: self.on_combo_box_changed(field, combo_box))
        combo_box_layout.addWidget(combo_box, 0, j)

    def on_combo_box_changed(self, field, combo_box):
        self.res_multi_choice[field["name"]] = None
        if combo_box.currentIndex() > 0:
            self.res_multi_choice[field["name"]] = combo_box.currentText()

    def create_address_layout(self):
        address_layout = QGridLayout()
        self.create_address_text_boxes(address_layout)
        self.create_map(address_layout)
        return address_layout

    def create_address_text_boxes(self, address_layout):
        coor_layout = QGridLayout()
        coor_layout.setContentsMargins(0, 50, 50, 50)
        self.create_text_label(coor_layout, "Please enter your city and street below", 0, 0)
        self.city_text_box = self.create_address_text_box(coor_layout, "Enter city", 1, 0)
        self.street_text_box = self.create_address_text_box(coor_layout, "Enter street", 2, 0)
        self.create_text_label(coor_layout, "Then find your coordinates in the map and enter them below", 3, 0)
        self.geo_loc_text_box = self.create_address_text_box(coor_layout, "Enter coordinates", 4, 0)
        address_layout.addLayout(coor_layout, 0, 0)

    def create_map(self, address_layout):
        def_location = (self.config["default_location"]["lat"], self.config["default_location"]["lng"])
        gmap = folium.Map(zoom_start=11, location=def_location)
        data = io.BytesIO()
        gmap.add_child(folium.LatLngPopup())
        gmap.save(data, close_file=False)

        web_view = QWebEngineView()
        web_view.setHtml(data.getvalue().decode())
        address_layout.addWidget(web_view, 0, 1)

    def create_activity_hours_layout(self):
        activity_hours_layout = QGridLayout()
        activity_hours_layout.setSpacing(10)
        days = self.config["days"]
        for idx, day in enumerate(days):
            self.create_activity_hours_labels(activity_hours_layout, idx, day)
        for idx, field in enumerate(self.open_fields):
            self.create_activity_widget(activity_hours_layout, 2, idx, self.res_activity[field["name"]], field)
        for idx, field in enumerate(self.close_fields):
            self.create_activity_widget(activity_hours_layout, 4, idx, self.res_activity[field["name"]], field)

        return activity_hours_layout

    def create_activity_hours_labels(self, activity_hours_layout, day, label_day):
        full_label = "Enter " + label_day + " activity"
        self.create_text_label(activity_hours_layout, full_label, 0, day)
        self.create_text_label(activity_hours_layout, "from:", 1, day)
        self.create_text_label(activity_hours_layout, "to:", 3, day)

    def create_activity_widget(self, activity_hours_layout, row, day, init_value, field):
        activity_time = QTimeEdit(self)
        init_time = Time(total_minutes=init_value)
        default = QTime(init_time.hours, init_time.minutes)
        activity_time.setTime(default)
        activity_time.editingFinished.connect(lambda: self.update_activity_hours(activity_time, field))
        activity_hours_layout.addWidget(activity_time, row, day)

    def update_activity_hours(self, activity_time, field):
        value = activity_time.time().toPyTime()
        self.res_activity[field["name"]] = Time(hours=value.hour, minutes=value.minute).get_total_minutes()

    def update_location_data(self):
        self.res_location["city"] = None if self.city_text_box.text() == '' else self.city_text_box.text()
        self.res_location["street"] = None if self.street_text_box.text() == '' else self.street_text_box.text()
        self.res_location["geo_location"] = None if self.geo_loc_text_box.text() == '' else [float(s) for s in self.geo_loc_text_box.text().split() if s.replace('.', '', 1).isdigit()]

    def set_info(self):
        self.res.update(self.res_bool)
        self.res.update(self.res_multi_choice)
        self.res.update(self.res_location)
        self.res.update(self.res_activity)

    def build_buttons(self):
        calculate_button = self.build_button("Calculate", self.on_calculate_clicked, 4, align_center=True)
        calculate_button.setFixedSize(500, 50)
        calculate_button.setStyleSheet("padding: 0px;")

        return_button = self.build_button("Go Back To Main Screen", self.on_return_clicked, 6, align_center=True)
        return_button.setFixedSize(400, 50)
        return_button.setStyleSheet("padding: 0px;")

    def on_calculate_clicked(self):
        self.update_location_data()
        self.set_info()
        if None in [self.res[key] for key in self.res if key != "type"]:
            self.show_error_message_box(("Error", "One or more of the fields are empty\nPlease fill in the missing values"))
        else:
            self.on_calc_clicked()

    @staticmethod
    def create_text_label(layout, text, i, j):
        label = QLabel(text)
        layout.addWidget(label, i, j)

    @staticmethod
    def create_address_text_box(layout, text, i, j, width=1):
        text_box = QLineEdit()
        text_box.setPlaceholderText(text)
        layout.addWidget(text_box, i, j, 1, width)
        return text_box
