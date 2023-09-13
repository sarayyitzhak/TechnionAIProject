import numpy as np
import pandas as pd
from SourceCode.Server.Algo.DecisonTree import *


class Prediction:
    def __init__(self):
        self.tree_root = None

    def create_decision_tree(self, formatted_decision_tree):
        self.tree_root = dict_to_node(formatted_decision_tree)

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
