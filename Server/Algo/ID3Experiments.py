import ast

from Server.Algo.ID3 import *
import pandas as pd


class ID3Experiments:

    def __init__(self):
        pass

    def basic_experiment(self):
        unneeded_labels = ["name", "user_ratings_total", "reviews_words", "city", "street"]
        attributes_names = list(pd.read_csv("./Dataset/data.csv", delimiter=",", dtype=str, nrows=1).keys())

        bool_cols = ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch',
                     'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout',
                     'wheelchair_accessible_entrance', 'curbside_pickup']
        activity_hours_cols = ["sunday_activity_hours", "monday_activity_hours", "tuesday_activity_hours",
                               "wednesday_activity_hours", "thursday_activity_hours", "friday_activity_hours",
                               "saturday_activity_hours"]
        for label in unneeded_labels:
            attributes_names.remove(label)
        train_set = pd.read_csv("./Dataset/data.csv")
        # for col in bool_cols:
        #     t = len([x for x in (train_set[col] == True) if x == True])
        #     f = len([x for x in (train_set[col] == False) if x == True])
        #     print(col + " TRUE: " + str(t) + " FALSE: " + str(f) + " BLANK: " + str(1414 - t - f))

        train_set.drop(unneeded_labels, axis='columns', inplace=True)
        # for col in bool_cols:
        #     train_set[col] = train_set[col].apply(lambda x: False if np.isnan(x) else x)
        for col in activity_hours_cols:
            train_set[col] = train_set[col].apply(lambda x: () if len(eval(x)) == 0 else (eval(x)[0], eval(x)[1]))

        train_set = train_set.replace({np.nan: None})
        msk = np.random.rand(len(train_set)) < 0.9
        train = train_set[msk]
        test = train_set[~msk]
        x_train = np.array(train.drop('rating', axis=1).copy())
        y_train = np.array(train['rating'].copy())
        x_test = np.array(test.drop('rating', axis=1).copy())
        y_test = np.array(test['rating'].copy())
        id3 = ID3(attributes_names, 10)
        id3.fit(x_train, y_train)
        self.print_tree(id3.tree_root)
        preds = id3.predict(x_test)

        print("\n\nPreds: " + str([(y_test[idx], preds[idx]) for idx in range(len(preds))]))
        print("Acc: " + str(100 * sum([math.fabs(y_test[idx] - preds[idx]) for idx in range(len(preds))]) / len(preds)))

    def print_tree(self, node, level=0):
        if isinstance(node, Leaf):
            avg = sum([float(key) * value for key, value in node.predictions.items()])
            sum_k = sum(node.predictions.values())
            print(' ' * 4 * level + '-> ' + str(avg / sum_k))

        if isinstance(node, DecisionNode):
            self.print_tree(node.true_branch, level + 1)
            print(' ' * 4 * level + '-> ' + str(node))
            self.print_tree(node.false_branch, level + 1)
