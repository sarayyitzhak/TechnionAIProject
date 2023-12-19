import numpy as np
from SourceCode.Server.Core.DecisionTree import *


class Prediction:
    def __init__(self, tree_root=None):
        self.tree_root = tree_root

    def create_decision_tree(self, formatted_decision_tree):
        self.tree_root = dict_to_node(formatted_decision_tree)

    def score(self, rows, labels):
        return (100 - (np.mean(np.abs(labels - self.predict(rows))))) / 100

    def score_MSE(self, rows, labels):
        return (np.sum((labels - self.predict(rows)) ** 2)) / len(labels)

    def predict(self, rows):
        return np.array([self.predict_sample(row).value for row in rows])

    def predict_sample(self, row, node: DecisionNode or Leaf = None):
        if node is None:
            node = self.tree_root

        if isinstance(node, Leaf):
            return node

        if isinstance(node, DecisionNode):
            if pd.isnull(row[node.question.column_idx]):
                true_leaf = self.predict_sample(row, node.true_branch)
                false_leaf = self.predict_sample(row, node.false_branch)
                total_size = true_leaf.size + false_leaf.size
                total_value = (true_leaf.value * true_leaf.size) + (false_leaf.value * false_leaf.size)
                total_mae = (true_leaf.mae * true_leaf.size) + (false_leaf.mae * false_leaf.size)
                return Leaf(total_value / total_size, total_size, total_mae / total_size)
            else:
                branch = node.true_branch if node.question.match(row) else node.false_branch
                return self.predict_sample(row, branch)
