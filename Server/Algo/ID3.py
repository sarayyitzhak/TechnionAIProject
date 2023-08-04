import math
import numpy as np
import pandas as pd

from Server.Algo.DecisonTree import *


class ID3:
    def __init__(self, fields, min_for_pruning=0, max_depth=10, progress_func=None):
        self.fields = fields
        self.tree_root = None
        self.min_for_pruning = min_for_pruning
        self.max_depth = max_depth
        self.progress_func = progress_func
        self.total_size = 0

    def fit(self, x_train, y_train):
        for idx, field in enumerate(self.fields):
            self.total_size += len(unique_vals(x_train, idx))
        self.total_size *= self.max_depth
        self.tree_root = self.build_tree(x_train, y_train, list(), 0, np.zeros(len(y_train)))

    def build_tree(self, rows, labels, used_questions, depth, w):
        total_w = np.sum(w)
        if total_w == 0:
            mean = np.mean(labels)
        else:
            mean = np.sum((labels * w) / total_w)
        mae = np.mean(np.abs(labels - mean)) / 100
        size = len(labels)

        if size <= self.min_for_pruning or depth >= self.max_depth or mae < 0.01:
            if depth < self.max_depth:
                self.total_size -= size
            return Leaf(mean, size, mae)

        best_partition = self.find_best_split(rows, labels, used_questions, w)
        self.total_size += (len(best_partition[2]) + len(best_partition[4])) - size
        best_question = best_partition[1]
        true_branch = self.build_tree(best_partition[2], best_partition[3], used_questions + [best_question], depth + 1, best_partition[6])
        false_branch = self.build_tree(best_partition[4], best_partition[5], used_questions + [best_question], depth + 1, best_partition[7])

        return DecisionNode(best_question, true_branch, false_branch)

    def find_best_split(self, rows, labels, used_questions, w):
        best_var = math.inf  # keep track of the best information gain
        best_question = None  # keep train of the feature / value that produced it
        best_false_rows, best_false_labels = None, None
        best_true_rows, best_true_labels = None, None
        best_true_w, best_false_w = None, None

        for idx, field in enumerate(self.fields):
            for val in unique_vals(rows, idx):
                question = Question(field["name"], field["type"], idx, val)
                if question in used_questions:
                    continue
                variance, true_rows, true_labels, false_rows, false_labels, true_w, false_w = self.partition(rows, labels, question, w)
                if variance < best_var:
                    best_var = variance
                    best_question = question
                    best_true_rows = true_rows
                    best_true_labels = true_labels
                    best_false_rows = false_rows
                    best_false_labels = false_labels
                    best_true_w = true_w
                    best_false_w = false_w
                if self.progress_func is not None:
                    self.progress_func(f"{field['name']}: {str(val)}", self.total_size)

        return best_var, best_question, best_true_rows, best_true_labels, best_false_rows, best_false_labels, best_true_w, best_false_w

    def partition(self, rows, labels, question: Question, w):
        variance, true_rows, true_labels, false_rows, false_labels = None, [], [], [], []
        true_w, false_w = [], []

        for idx, row in enumerate(rows):
            if pd.isnull(row[question.column_idx]):
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
                true_w.append(w[idx])
                false_rows.append(row)
                false_labels.append(float(labels[idx]))
                false_w.append(w[idx])
            elif question.match(row):
                true_rows.append(row)
                true_labels.append(float(labels[idx]))
                true_w.append(w[idx] + 1)
            else:
                false_rows.append(row)
                false_labels.append(float(labels[idx]))
                false_w.append(w[idx] + 1)

        true_rows = np.array(true_rows)
        true_labels = np.array(true_labels)
        false_rows = np.array(false_rows)
        false_labels = np.array(false_labels)
        variance = self.variance_reduction(true_labels, false_labels)

        return variance, true_rows, true_labels, false_rows, false_labels, np.array(true_w), np.array(false_w)

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

    def score(self, rows, labels):
        return (100 - (np.mean(np.abs(labels - self.predict(rows))))) / 100

    def score_MSE(self, rows, labels):
        return (np.sum((labels - self.predict(rows)) ** 2)) / len(labels)

    def predict(self, rows, return_none_values=False):
        return np.array([self.predict_sample(row, return_none_values) for row in rows])

    def predict_sample(self, row, return_none_values, node: DecisionNode or Leaf = None):
        if node is None:
            node = self.tree_root

        if isinstance(node, Leaf):
            return node.value

        if isinstance(node, DecisionNode):
            if return_none_values and pd.isnull(row[node.question.column_idx]):
                return None
            branch = node.true_branch if node.question.match(row) else node.false_branch
            return self.predict_sample(row, return_none_values, branch)
