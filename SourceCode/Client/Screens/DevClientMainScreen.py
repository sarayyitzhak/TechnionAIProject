from PyQt5.QtWidgets import *

from SourceCode.Client.Screens.Screen import Screen
from SourceCode.Client.Workers.DataParserWorker import *
from SourceCode.Client.Workers.GoogleDataBuilderWorker import *
from SourceCode.Client.Workers.RestDataBuilderWorker import *
from SourceCode.Client.Workers.CbsDataBuilderWorker import *
from SourceCode.Client.Workers.GovDataBuilderWorker import *
from SourceCode.Client.Workers.RunAlgorithmWorker import *
from SourceCode.Client.Workers.ProdConfigDataCreatorWorker import *
from SourceCode.Client.Workers.FindHyperParamsWorker import *
from SourceCode.Client.Workers.Worker import *
from SourceCode.Server.Algo.ShowHyperParamsAnalysis import *


class DevClientMainScreen(Screen):
    def __init__(self, on_return_clicked):
        super().__init__()

        self.on_return_clicked = on_return_clicked

        self.scroll: QScrollArea = None
        self.scroll_layout: QVBoxLayout = None

        self.thread_pool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        self.build_buttons()
        self.build_scroll_bar()

    def build_buttons(self):
        self.build_button("Build Google Data", self.on_build_google_clicked, 0, 0, 1)
        self.build_button("Build Rest Data", self.on_build_rest_clicked, 0, 1, 1)
        self.build_button("Build CBS Data", self.on_build_cbs_clicked, 0, 2, 1)
        self.build_button("Build Gov Data", self.on_build_gov_clicked, 0, 3, 1)
        self.build_button("Build All Data", self.on_build_all_clicked, 1, 0, 4)
        self.build_button("Parse Data", self.on_parse_data_clicked, 2, 0, 4)
        self.build_button("Create Production Data Config", self.on_data_config_clicked, 3, 0, 4)
        self.build_button("Find Hyper Params", self.on_find_hyper_params_clicked, 4, 0, 4)
        self.build_button("Show Validation Analysis", self.on_show_valid_analysis_clicked, 5, 0, 1)
        self.build_button("Show Train Analysis", self.on_show_train_analysis_clicked, 5, 1, 1)
        self.build_button("Show Validation MSE Analysis", self.on_show_valid_mse_analysis_clicked, 5, 2, 1)
        self.build_button("Show Train MSE Analysis", self.on_show_train_mse_analysis_clicked, 5, 3, 1)
        self.build_button("Run Algorithm", self.on_run_alg_clicked, 6, 0, 4)
        self.build_button("Go Back To Main Screen", self.on_return_clicked, 8, 0, 4)

    def build_scroll_bar(self):
        self.scroll = QScrollArea()
        widget = QWidget()
        self.scroll_layout = QVBoxLayout(widget)
        self.scroll.setWidget(widget)

        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(150)

        self.layout.addWidget(self.scroll, 7, 0, 1, 4)
        self.scroll.hide()

    def on_build_google_clicked(self):
        self.on_button_clicked(GoogleDataBuilderWorker('./ConfigFiles/google-data-config.json'))

    def on_build_rest_clicked(self):
        self.on_button_clicked(RestDataBuilderWorker('./ConfigFiles/rest-data-config.json'))

    def on_build_cbs_clicked(self):
        self.on_button_clicked(CbsDataBuilderWorker('./ConfigFiles/cbs-data-config.json'))

    def on_build_gov_clicked(self):
        self.on_button_clicked(GovDataBuilderWorker('./ConfigFiles/gov-data-config.json'))

    def on_build_all_clicked(self):
        self.on_build_google_clicked()
        self.on_build_rest_clicked()
        self.on_build_cbs_clicked()
        self.on_build_gov_clicked()

    def on_data_config_clicked(self):
        self.on_button_clicked(ProdConfigDataCreatorWorker('./ConfigFiles/prod-data-creator-config.json'))

    def on_parse_data_clicked(self):
        self.on_button_clicked(DataParserWorker('./ConfigFiles/data-parser-config.json'))

    def on_find_hyper_params_clicked(self):
        self.on_button_clicked(FindHyperParamsWorker('./ConfigFiles/find-hyper-params-config.json'))

    def on_show_valid_analysis_clicked(self):
        self.on_show_hyper_params_analysis_clicked('VALIDATION')

    def on_show_train_analysis_clicked(self):
        self.on_show_hyper_params_analysis_clicked('TRAIN')

    def on_show_valid_mse_analysis_clicked(self):
        self.on_show_hyper_params_analysis_clicked('VALIDATION_MSE')

    def on_show_train_mse_analysis_clicked(self):
        self.on_show_hyper_params_analysis_clicked('TRAIN_MSE')

    @staticmethod
    def on_show_hyper_params_analysis_clicked(y_axis_type):
        with open('./ConfigFiles/show-hyper-params-analysis-config.json', 'r', encoding='utf-8') as f:
            show_hyper_params_analysis = ShowHyperParamsAnalysis(json.load(f), y_axis_type)
            show_hyper_params_analysis.pre_show_hyper_params_analysis()
            show_hyper_params_analysis.show_hyper_params_analysis()

    def on_run_alg_clicked(self):
        self.on_button_clicked(RunAlgorithmWorker('./ConfigFiles/algo-config.json'))

    def on_button_clicked(self, worker):
        group_box = QGroupBox()
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        title = QLabel()
        subtitle = QLabel()
        actual_time = QLabel()
        estimated_time = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(progress_bar)
        layout.addWidget(actual_time)
        layout.addWidget(estimated_time)
        group_box.setLayout(layout)

        self.scroll_layout.addWidget(group_box)
        self.scroll.show()

        worker.signals.progress.connect(progress_bar.setValue)
        worker.signals.title.connect(title.setText)
        worker.signals.subtitle.connect(subtitle.setText)
        worker.signals.actual_time.connect(actual_time.setText)
        worker.signals.estimated_time.connect(estimated_time.setText)
        worker.signals.error.connect(self.show_error_message_box)
        worker.signals.finished.connect(lambda: self.on_worker_finished(group_box))

        self.thread_pool.start(worker)

    def on_worker_finished(self, widget):
        self.scroll_layout.removeWidget(widget)
        if self.thread_pool.activeThreadCount() == 0:
            self.scroll.hide()
