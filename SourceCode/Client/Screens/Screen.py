from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Screen(QDialog):
    def __init__(self):
        super().__init__()

        self.layout: QGridLayout = None
        self.init_screen()

    def init_screen(self):
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet('QPushButton {padding: 5ex; margin: 2ex;}')

        widget = QWidget()
        self.layout = QGridLayout(widget)

        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)

        screen_layout = QGridLayout()
        screen_layout.addWidget(scroll)
        self.setLayout(screen_layout)

    def build_button(self, label, function, row, column=0, column_span=1, row_span=1, align_center=False):
        button = QPushButton(label)
        button.clicked.connect(function)
        if align_center:
            self.layout.addWidget(button, row, column, row_span, column_span, Qt.AlignCenter)
        else:
            self.layout.addWidget(button, row, column, row_span, column_span)
        return button

    @staticmethod
    def show_error_message_box(value=None):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An error occurred" if value is None else value[1])
        msg.setWindowTitle("Error" if value is None else value[0])
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
