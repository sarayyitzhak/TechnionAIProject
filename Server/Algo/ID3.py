import math
import numpy as np

from Server.Algo.DecisonTree import *


class ID3:
    def __init__(self, label_names: list, min_for_pruning=0, target_attribute='rating'):
        self.label_names = label_names
        self.target_attribute = target_attribute
        self.tree_root = None
        self.used_features = set()
        self.min_for_pruning = min_for_pruning

    @staticmethod
    def variance_reduction(left, left_labels, right, right_labels):
        assert (len(left) == len(left_labels)) and (len(right) == len(right_labels)), \
            'The split of current node is not right, rows size should be equal to labels size.'
        len_left = len(left_labels)
        len_right = len(right_labels)
        total_len = len_right + len_left
        if len_right == 0 or len_left == 0:
            return math.inf
        mean_of_left_child = sum(left_labels) / len_left
        mean_of_right_child = sum(right_labels) / len_right
        var_sum = 0

        for label in left_labels:
            var_sum += (mean_of_left_child - label) ** 2
        var_left = var_sum
        var_sum = 0
        for label in right_labels:
            var_sum += (mean_of_right_child - label) ** 2
        var_right = var_sum

        var = ((1 / total_len) * var_left) + ((1 / total_len) * var_right)
        return var

    def partition(self, rows, labels, question: Question):
        variance, true_rows, true_labels, false_rows, false_labels = None, [], [], [], []
        assert len(rows) == len(labels), 'Rows size should be equal to labels size.'

        for idx, row in enumerate(rows):
            if row[question.column_idx] is None:
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
                false_rows.append(row)
                false_labels.append(float(labels[idx]))
            elif question.match(row):
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
            else:
                false_rows.append(row)
                false_labels.append(float(labels[idx]))

        true_rows = np.array(true_rows)
        true_labels = np.array(true_labels)
        false_rows = np.array(false_rows)
        false_labels = np.array(false_labels)
        variance = self.variance_reduction(true_rows, true_labels, false_rows, false_labels)

        return variance, true_rows, true_labels, false_rows, false_labels

    def find_best_split(self, rows, labels):
        best_var = math.inf  # keep track of the best information gain
        best_question = None  # keep train of the feature / value that produced it
        best_false_rows, best_false_labels = None, None
        best_true_rows, best_true_labels = None, None

        for idx, label_name in enumerate([name for name in self.label_names if name != self.target_attribute]):
            for val in unique_vals(rows, idx):
                if val is None:
                    continue
                question = Question(label_name, idx, val)
                variance, true_rows, true_labels, false_rows, false_labels = self.partition(rows, labels, question)
                question.var = variance
                if variance < best_var:
                    best_var = variance
                    best_question = question
                    best_true_rows = true_rows
                    best_true_labels = true_labels
                    best_false_rows = false_rows
                    best_false_labels = false_labels

        return best_var, best_question, best_true_rows, best_true_labels, best_false_rows, best_false_labels

    def build_tree(self, rows, labels):
        leaf = Leaf(rows, labels)

        if len(rows) <= self.min_for_pruning or max(leaf.predictions) - min(leaf.predictions) <= 0.3:
            return leaf

        best_partition = self.find_best_split(rows, labels)
        best_question = best_partition[1]
        true_branch = self.build_tree(best_partition[2], best_partition[3])
        false_branch = self.build_tree(best_partition[4], best_partition[5])

        return DecisionNode(best_question, true_branch, false_branch)

    def fit(self, x_train, y_train):
        self.tree_root = self.build_tree(x_train, y_train)

    def predict_sample(self, row, node: DecisionNode or Leaf = None):
        """
        Predict the most likely class for single sample in subtree of the given node.
        :param row: vector of shape (1,D).
        :return: The row prediction.
        """
        # TODO: Implement ID3 class prediction for set of data.
        #   - Decide whether to follow the true-branch or the false-branch.
        #   - Compare the feature / value stored in the node, to the example we're considering.

        if node is None:
            node = self.tree_root

        if isinstance(node, Leaf):
            if len(node.predictions) == 1:
                return list(node.predictions.keys())[0]
            else: # avg of all results
                avg = 0
                sum_k = 0
                for key, value in node.predictions.items():
                    avg += float(key) * value
                    sum_k += value
                return avg / sum_k

        if isinstance(node, DecisionNode):
            branch = node.true_branch if node.question.match(row) else node.false_branch
            return self.predict_sample(row, branch)

    def predict(self, rows):
        return np.array([self.predict_sample(row) for row in rows])
