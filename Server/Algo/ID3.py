import math
import numpy as np

from Server.Algo.DecisonTree import *


class ID3:
    def __init__(self, label_names: list, min_for_pruning=0, max_depth=10, target_attribute='rating'):
        self.label_names = label_names
        self.target_attribute = target_attribute
        self.tree_root = None
        self.used_features = set()
        self.min_for_pruning = min_for_pruning
        self.max_depth = max_depth

    @staticmethod
    def variance_reduction(left_labels, right_labels):
        len_left = len(left_labels)
        len_right = len(right_labels)
        total_len = len_right + len_left
        if len_right == 0 or len_left == 0:
            return math.inf
        mean_of_left_child = np.mean(left_labels)
        mean_of_right_child = np.mean(right_labels)

        var_left = np.mean((left_labels - mean_of_left_child) ** 2)
        var_right = np.mean((right_labels - mean_of_right_child) ** 2)

        return ((len_left / total_len) * var_left) + ((len_right / total_len) * var_right)

    def partition(self, rows, labels, question: Question):
        variance, true_rows, true_labels, false_rows, false_labels = None, [], [], [], []

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
        variance = self.variance_reduction(true_labels, false_labels)

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

    def build_tree(self, rows, labels, depth=0):
        leaf = Leaf(labels)

        if len(rows) <= self.min_for_pruning or depth >= self.max_depth or leaf.mse < 0.1:
            return leaf

        best_partition = self.find_best_split(rows, labels)
        best_question = best_partition[1]
        true_branch = self.build_tree(best_partition[2], best_partition[3], depth + 1)
        false_branch = self.build_tree(best_partition[4], best_partition[5], depth + 1)

        return DecisionNode(best_question, true_branch, false_branch)

    def fit(self, x_train, y_train):
        self.tree_root = self.build_tree(x_train, y_train)

    def predict_sample(self, row, node: DecisionNode or Leaf = None):
        if node is None:
            node = self.tree_root

        if isinstance(node, Leaf):
            return node.mean

        if isinstance(node, DecisionNode):
            branch = node.true_branch if node.question.match(row) else node.false_branch
            return self.predict_sample(row, branch)

    def predict(self, rows):
        return np.array([self.predict_sample(row) for row in rows])
