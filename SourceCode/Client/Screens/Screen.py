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

        screen_layout = QGridLayout()

        scroll = QScrollArea()
        widget = QWidget()
        self.layout = QGridLayout(widget)
        scroll.setWidget(widget)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setWidgetResizable(True)

        screen_layout.addWidget(scroll)

        # screen_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(screen_layout)

    def build_button(self, label, function, row, column=0, column_span=1, align_center=False):
        return self.build_button_for_layout(self.layout, label, function, row, column, column_span, align_center)

    @staticmethod
    def build_button_for_layout(layout: QGridLayout, label, function, row, column=0, column_span=1, align_center=False):
        button = QPushButton(label)
        button.clicked.connect(function)
        if align_center:
            layout.addWidget(button, row, column, 1, column_span, Qt.AlignCenter)
        else:
            layout.addWidget(button, row, column, 1, column_span)
        return button
