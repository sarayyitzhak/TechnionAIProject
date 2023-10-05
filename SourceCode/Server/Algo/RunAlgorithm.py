from SourceCode.Server.Algo.ID3Experiments import *
from SourceCode.Server.Utils.FileUtils import write_to_file
from SourceCode.Server.Algo.AlgoUtils import *


class RunAlgorithm:
    def __init__(self, config, progress_func):
        self.data_set_path = config["data_set_path"]
        self.target_field = config["target_field"]
        self.min_for_pruning = config["min_for_pruning"]
        self.max_depth = config["max_depth"]
        self.min_samples_leaf = config["min_samples_leaf"]
        self.fields = config["fields"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.data = None
        self.regressor = None

    def pre_run_algo(self):
        self.data = get_data(self.data_set_path, self.fields, self.target_field)

    def run_algo(self):
        self.regressor = DecisionTreeRegressor(self.fields, self.min_for_pruning, self.max_depth, self.min_samples_leaf, self.progress_func)
        x_train = np.array(self.data.drop(self.target_field, axis=1).copy())
        y_train = np.array(self.data[self.target_field].copy())
        self.regressor.fit(x_train, y_train)

    def save_data(self):
        write_to_file(node_to_dict(self.regressor.tree_root), self.output_path)
