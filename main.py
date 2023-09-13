from SourceCode.Client.Screens.DevClientMainScreen import *
from SourceCode.Client.Windows.ProdClientMainWindow import ProdClientMainWindow


def main():
    ## DEV
    # dev_client_app = QApplication([])
    # dev_client_app_window = DevClientMainWindow()
    # dev_client_app_window.show()
    # dev_client_app.exec()
    ## PROD
    prod_client_app = QApplication([])
    main_window = ProdClientMainWindow()
    prod_client_app.exec()


if __name__ == '__main__':
    main()



