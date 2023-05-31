from Server.Algo.ID3Experiments import *


class RunAlgorithm:
    def __init__(self, config, progress_func):
        self.data_set_path = config["data_set_path"]
        self.target_field = config["target_field"]
        self.min_for_pruning = config["min_for_pruning"]
        self.max_depth = config["max_depth"]
        self.fields = config["fields"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.data = None
        self.algo = None

    def pre_run_algo(self):
        self.data = pd.read_csv(self.data_set_path)
        field_names = [field["name"] for field in self.fields] + [self.target_field]
        self.data = self.data[field_names]

        for col in [field["name"] for field in self.fields if field["type"] in ["ACTIVITY_HOURS", "GEO_LOCATION"]]:
            self.data[col] = self.data[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

    def run_algo(self):
        self.algo = ID3(self.fields, self.min_for_pruning, self.max_depth, self.progress_func)
        x_train = np.array(self.data.drop(self.target_field, axis=1).copy())
        y_train = np.array(self.data[self.target_field].copy())
        self.algo.fit(x_train, y_train)

    def save_data(self):
        write_to_file(node_to_dict(self.algo.tree_root), self.output_path)
