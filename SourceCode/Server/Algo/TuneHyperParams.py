from SourceCode.Server.Algo.DecisionTreeRegressor import *
from SourceCode.Server.Algo.Prediction import *
from SourceCode.Server.Algo.AlgoUtils import *
import numpy as np


class TuneHyperParams:
    def __init__(self, config, progress_func):
        self.data_set_path = config["data_set_path"]
        self.target_field = config["target_field"]
        self.min_for_pruning_values = config["min_for_pruning_values"]
        self.max_depth_values = config["max_depth_values"]
        self.min_samples_leaf_values = config["min_samples_leaf_values"]
        self.k = config["k_value"]
        self.fields = config["fields"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.data = None
        self.result = []

    def pre_find_hyper_params(self):
        self.data = get_data(self.data_set_path, self.fields, self.target_field)

    def find_hyper_params(self):
        k_fold_idx = self.data.index % self.k
        hyper_params = [(x, y, z) for x in self.min_for_pruning_values for y in self.max_depth_values for z in self.min_samples_leaf_values]

        for min_for_pruning, max_depth, min_samples_leaf in hyper_params:
            train_scores = 0
            train_scores_MSE = 0
            valid_scores = 0
            valid_scores_MSE = 0
            for fold in range(self.k):
                if self.progress_func is not None:
                    self.progress_func(f"Fold: {fold} | Min For Pruning: {min_for_pruning} | Max Depth: {max_depth} | Min Samples Leaf: {min_samples_leaf}", self.k * len(hyper_params))
                train_fold = self.data[k_fold_idx != fold]
                validation_fold = self.data[k_fold_idx == fold]
                x_train_fold = np.array(train_fold.drop(self.target_field, axis=1).copy())
                y_train_fold = np.array(train_fold[self.target_field].copy())
                x_validation_fold = np.array(validation_fold.drop(self.target_field, axis=1).copy())
                y_validation_fold = np.array(validation_fold[self.target_field].copy())
                regressor = DecisionTreeRegressor(self.fields, min_for_pruning, max_depth, min_samples_leaf, None)
                regressor.fit(x_train_fold, y_train_fold)
                prediction = Prediction(regressor.tree_root)
                train_scores += prediction.score(x_train_fold, y_train_fold)
                train_scores_MSE += prediction.score_MSE(x_train_fold, y_train_fold)
                valid_scores += prediction.score(x_validation_fold, y_validation_fold)
                valid_scores_MSE += prediction.score_MSE(x_validation_fold, y_validation_fold)
            self.result.append({
                "min for pruning": min_for_pruning,
                "max depth": max_depth,
                "min samples leaf": min_samples_leaf,
                "train acc": train_scores / self.k,
                "train MSE": train_scores_MSE / self.k,
                "valid acc": valid_scores / self.k,
                "valid MSE": valid_scores_MSE / self.k
            })

    def save_data(self):
        pd.DataFrame(self.result).to_csv(self.output_path, index=False, encoding='utf-8-sig')


