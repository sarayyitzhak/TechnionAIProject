import numpy as np
from SourceCode.Server.Algo.DecisonTree import *


class Prediction:
    def __init__(self):
        self.tree_root = None

    def create_decision_tree(self, formatted_decision_tree):
        self.tree_root = dict_to_node(formatted_decision_tree)

    def predict(self, rows):
        return np.array([self.predict_sample(row) for row in rows])

    def predict_sample(self, row, node: DecisionNode or Leaf = None):
        if node is None:
            node = self.tree_root

        if isinstance(node, Leaf):
            return node.value

        if isinstance(node, DecisionNode):
            if pd.isnull(row[node.question.column_idx]):
                return (self.predict_sample(row, node.true_branch) + self.predict_sample(row, node.false_branch)) / 2
            else:
                branch = node.true_branch if node.question.match(row) else node.false_branch
                return self.predict_sample(row, branch)
