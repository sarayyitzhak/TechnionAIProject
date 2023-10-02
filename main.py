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
    # t = [1,2,3,4,5,6]
    # t = np.array([]).reshape((0, 3))
    # t = np.append(t, [[5, 5, 6]], axis=0)
    # t = np.append(t, [[8, 7, 9]], axis=0)
    # print(np.mean(t))


if __name__ == '__main__':
    main()



