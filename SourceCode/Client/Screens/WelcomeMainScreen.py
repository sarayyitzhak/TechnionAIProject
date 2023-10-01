from SourceCode.Client.Screens.Screen import Screen


class WelcomeMainScreen(Screen):
    def __init__(self, on_dev_clicked, on_prod_clicked):
        super().__init__()

        self.on_dev_clicked = on_dev_clicked
        self.on_prod_clicked = on_prod_clicked
        self.init_ui()

    def init_ui(self):
        self.build_button("Development", self.on_dev_clicked, 0)
        self.build_button("Production", self.on_prod_clicked, 1)
