from Server.Algo.ID3 import *
import pandas as pd
import json

class ID3Experiments:

    def __init__(self):
        pass

    def basic_experiment(self):
        try:
            with open('./DataConfig/algo-config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                train_set = pd.read_csv(config["data_set_path"])
                field_names = [field["name"] for field in config["fields"]] + [config["target_field"]]
                train_set = train_set[field_names]

                for col in [field["name"] for field in config["fields"] if field["type"] in ["ACTIVITY_HOURS", "GEO_LOCATION"]]:
                    train_set[col] = train_set[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

                msk = np.random.rand(len(train_set)) < 0.9
                train = train_set[msk]
                test = train_set[~msk]
                x_train = np.array(train.drop(config["target_field"], axis=1).copy())
                y_train = np.array(train[config["target_field"]].copy())
                x_test = np.array(test.drop(config["target_field"], axis=1).copy())
                y_test = np.array(test[config["target_field"]].copy())
                id3 = ID3(config["fields"], config["min_for_pruning"], config["max_depth"])
                id3.fit(x_train, y_train)
                self.print_tree(id3.tree_root)
                preds = id3.predict(x_test)

                print("\n\nPreds: " + str([(y_test[idx], preds[idx]) for idx in range(len(preds))]))
                print("Acc: {:.2f}%".format(100 - (np.mean(np.abs(y_test - preds)))))

        except IOError:
            print("Error")

    def print_tree(self, node, level=0):
        if isinstance(node, Leaf):
            print(' ' * 4 * level + str(level) + '-> ' + str(node))

        if isinstance(node, DecisionNode):
            self.print_tree(node.true_branch, level + 1)
            print(' ' * 4 * level + str(level) + '-> ' + str(node))
            self.print_tree(node.false_branch, level + 1)
