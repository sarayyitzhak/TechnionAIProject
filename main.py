from Client.DevClient import *


def main():
    dev_client_app = QApplication([])
    dev_client_app_window = DevClientMainWindow()
    dev_client_app_window.show()
    dev_client_app.exec()


if __name__ == '__main__':
    main()



