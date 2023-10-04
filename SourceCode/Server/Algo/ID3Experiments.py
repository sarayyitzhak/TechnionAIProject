from SourceCode.Server.Algo.AlgoUtils import get_data
from SourceCode.Server.Algo.DecisionTreeRegressor import *
from SourceCode.Server.Algo.Prediction import *
import pandas as pd
import json
import matplotlib.pyplot as plt

class ID3Experiments:

    def __init__(self):
        pass

    def basic_experiment(self, config_path, msk):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                train_set = get_data(config["data_set_path"], config["fields"], config["target_field"])

                # msk = np.random.rand(len(train_set)) < 0.9
                train = train_set[msk]
                test = train_set[~msk]
                x_train = np.array(train.drop(config["target_field"], axis=1).copy())
                y_train = np.array(train[config["target_field"]].copy())
                x_test = np.array(test.drop(config["target_field"], axis=1).copy())
                y_test = np.array(test[config["target_field"]].copy())
                regressor = DecisionTreeRegressor(config["fields"], config["min_for_pruning"], config["max_depth"])
                regressor.fit(x_train, y_train)
                # self.print_tree(regressor.tree_root)
                # tree_file = open('./DataOutput/algo-tree.json', 'r', encoding='utf-8')
                # formatted_tree = json.load(tree_file)
                prediction = Prediction(regressor.tree_root)
                # prediction = Prediction()
                # prediction.create_decision_tree(formatted_tree)

                # preds = prediction.predict(x_test)
                print(f"Train Score: {prediction.score(x_train, y_train)}")
                print(f"Train MSE: {prediction.score_MSE(x_train, y_train)}")
                print(f"Score: {prediction.score(x_test, y_test)}")
                print(f"MSE: {prediction.score_MSE(x_test, y_test)}")

                # res = []
                # for idx, row in enumerate(x_test):
                #     sample = prediction.predict_sample(row)
                #     res.append({
                #         "pred": sample.value,
                #         "pred_mae": sample.mae,
                #         "grade": y_test[idx]
                #     })
                #
                # pd.DataFrame(res).to_csv("./DataOutput/test.csv", index=False, encoding='utf-8-sig')

                # plt.plot(list(range(len(x_test))), preds, 'o', color='r', label='preds')
                # plt.plot(list(range(len(x_test))), y_test, 'o', color='g', label='origs')
                # plt.legend()
                # plt.show()

        except IOError:
            print("Error")

    def print_tree(self, node, level=0):
        if isinstance(node, Leaf):
            print(' ' * 4 * level + str(level) + '-> ' + str(node))

        if isinstance(node, DecisionNode):
            self.print_tree(node.true_branch, level + 1)
            print(' ' * 4 * level + str(level) + '-> ' + str(node))
            self.print_tree(node.false_branch, level + 1)
