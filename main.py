from PyQt5.QtWidgets import *
from SourceCode.Client.Windows.AppMainWindow import AppMainWindow


def main():
    app = QApplication([])
    main_window = AppMainWindow()
    app.exec()


if __name__ == '__main__':
    main()



