import numpy as np

from SourceCode.Server.Algo.DecisonTree import *


class DecisionTreeRegressor:
    def __init__(self, fields, min_for_pruning=0, max_depth=10, progress_func=None):
        self.fields = fields
        self.tree_root = None
        self.min_for_pruning = min_for_pruning
        self.max_depth = max_depth
        self.progress_func = progress_func
        self.nodes = (2 ** max_depth) - 1

    def fit(self, x_train, y_train):
        self.tree_root = self.build_tree(x_train, y_train, np.zeros(len(y_train)), [])

    def build_tree(self, rows, labels, weights, used_questions, depth=0, print_str=""):
        total_weights = np.sum(weights)
        if total_weights == 0:
            mean = np.mean(labels)
        else:
            mean = np.sum(labels * weights) / total_weights
        mae = np.mean(np.abs(labels - mean)) / 100
        size = len(labels)

        if size <= self.min_for_pruning or depth >= self.max_depth or mae < 0.01:
            self.nodes -= (2 ** (self.max_depth - depth)) - 1
            return Leaf(mean, size, mae)

        best_partition = self.find_best_split(rows, labels, weights, used_questions, print_str)
        best_question = best_partition[0]
        new_print_str = f"{print_str} {best_question.column}[{best_question.value}] -> "
        true_branch = self.build_tree(best_partition[1], best_partition[2], best_partition[3], used_questions + [best_question], depth + 1, new_print_str)
        false_branch = self.build_tree(best_partition[4], best_partition[5], best_partition[6], used_questions + [best_question], depth + 1, new_print_str)

        return DecisionNode(best_question, true_branch, false_branch)

    def find_best_split(self, rows, labels, weights, used_questions, print_str):
        best_var = math.inf
        best_question = None
        best_true_rows, best_true_labels, best_true_weights = None, None, None
        best_false_rows, best_false_labels, best_false_weights = None, None, None

        for idx, field in enumerate(self.fields):
            if self.progress_func is not None:
                self.progress_func(f"{print_str}{field['name']}", self.nodes * len(self.fields))
            for val in unique_vals(rows, idx):
                question = Question(field["name"], field["type"], idx, val)
                if question in used_questions:
                    continue
                partition = self.partition(rows, labels, weights, question)
                if partition[0] < best_var:
                    best_var = partition[0]
                    best_question = question
                    best_true_rows = partition[1]
                    best_true_labels = partition[2]
                    best_true_weights = partition[3]
                    best_false_rows = partition[4]
                    best_false_labels = partition[5]
                    best_false_weights = partition[6]

        return best_question, np.array(best_true_rows), np.array(best_true_labels), np.array(best_true_weights), \
               np.array(best_false_rows), np.array(best_false_labels), np.array(best_false_weights)

    def partition(self, rows, labels, weights, question: Question):
        true_rows, true_labels, true_weights = [], [], []
        false_rows, false_labels, false_weights = [], [], []
        left_labels, right_labels = [], []

        for idx, row in enumerate(rows):
            if pd.isnull(row[question.column_idx]):
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
                true_weights.append(weights[idx])
                false_rows.append(row)
                false_labels.append(float(labels[idx]))
                false_weights.append(weights[idx])
            elif question.match(row):
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
                true_weights.append(weights[idx] + 1)
                left_labels.append(float(labels[idx]))
            else:
                false_rows.append(row)
                false_labels.append(float(labels[idx]))
                false_weights.append(weights[idx] + 1)
                right_labels.append(float(labels[idx]))

        variance = self.variance_reduction(np.array(left_labels), np.array(right_labels))

        return variance, true_rows, true_labels, true_weights, false_rows, false_labels, false_weights

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
