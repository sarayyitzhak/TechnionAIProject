from Server.Algo.ID3 import *
import pandas as pd
import numpy as np


class FindHyperParams:
    def __init__(self, config, progress_func):
        self.data_set_path = config["data_set_path"]
        self.target_field = config["target_field"]
        self.min_for_pruning = config["min_for_pruning"]
        self.max_depth = config["max_depth"]
        self.fields = config["fields"]
        self.output_path = config["output_path"]
        self.progress_func = progress_func
        self.k = 5
        self.min_for_pruning_values = [3, 10, 25, 50]
        self.max_depth_values = [3, 4, 5, 6, 7, 8, 9, 10]
        self.data = None

    def find_hyper_params(self):
        self.data = pd.read_csv(self.data_set_path)
        field_names = [field["name"] for field in self.fields] + [self.target_field]
        self.data = self.data[field_names]

        for col in [field["name"] for field in self.fields if field["type"] in ["ACTIVITY_HOURS", "GEO_LOCATION"]]:
            self.data[col] = self.data[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

        msk = np.random.rand(len(self.data)) < 0.9
        train = self.data[msk]
        test = self.data[~msk]

        k_fold_idx = train.index % self.k
        hyper_params = [(x, y) for x in self.min_for_pruning_values for y in self.max_depth_values]
        print(hyper_params)

        for min_for_pruning, max_depth in hyper_params:
            scores = 0
            scores_MSE = 0
            for fold in range(self.k):
                train_fold = train[k_fold_idx != fold]
                validation_fold = train[k_fold_idx == fold]
                x_train_fold = np.array(train_fold.drop(self.target_field, axis=1).copy())
                y_train_fold = np.array(train_fold[self.target_field].copy())
                x_validation_fold = np.array(validation_fold.drop(self.target_field, axis=1).copy())
                y_validation_fold = np.array(validation_fold[self.target_field].copy())
                algo = ID3(self.fields, min_for_pruning, max_depth, None)
                algo.fit(x_train_fold, y_train_fold)
                score = algo.score(x_validation_fold, y_validation_fold)
                score_MSE = algo.score_MSE(x_validation_fold, y_validation_fold)
                print(f"Fold: {fold} ValidScore: {round(score, 3)} ValidMSE: {round(score_MSE, 3)} min_for_pruning: {min_for_pruning} max_depth: {max_depth}")
                print(f"Fold: {fold} TrainScore: {round(algo.score(x_train_fold, y_train_fold), 3)} TrainMSE: {round(algo.score_MSE(x_train_fold, y_train_fold), 3)} min_for_pruning: {min_for_pruning} max_depth: {max_depth}")
                scores += score
                scores_MSE += score_MSE
            print(f"Total ValidScore: {round(scores / self.k, 3)} ValidMSE: {round(scores_MSE / self.k, 3)} min_for_pruning: {min_for_pruning} max_depth: {max_depth}")


