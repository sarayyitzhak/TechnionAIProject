import pandas as pd
import math
from SourceCode.Server.Utils.Utils import *


def unique_vals(rows, col):
    vals = set([row[col] for row in rows if not pd.isnull(row[col])])
    if len(vals) <= 100:
        return vals
    else:
        ceil = math.ceil(len(vals) / 100)
        return [val for idx, val in enumerate(sorted(vals)) if idx % ceil == 0]


def node_to_dict(node):
    if isinstance(node, Leaf):
        return {
            "value": node.value,
            "size": node.size,
            "mae": node.mae
        }

    if isinstance(node, DecisionNode):
        return {
            "question": {
                "column": node.question.column,
                "field_type": node.question.field_type,
                "column_idx": node.question.column_idx,
                "value": node.question.value
            },
            "false": node_to_dict(node.false_branch),
            "true": node_to_dict(node.true_branch)
        }


def dict_to_node(node):
    if "question" in node:
        q = node["question"]
        value = tuple(q["value"]) if q["field_type"] in ["ACTIVITY_HOURS", "GEO_LOCATION"] else q["value"]
        question = Question(q["column"], q["field_type"], q["column_idx"], value)
        return DecisionNode(question, dict_to_node(node["true"]), dict_to_node(node["false"]))
    else:
        return Leaf(node["value"], node["size"], node["mae"])


class Question:

    def __init__(self, column, field_type, column_idx, value):
        self.column = column
        self.field_type = field_type
        self.column_idx = column_idx
        self.value = value

    def match(self, example):
        val = example[self.column_idx]
        if pd.isnull(val):
            return False
        if self.field_type == "GEO_LOCATION":
            return is_closes_places(self.value, val)
        elif self.field_type == "ACTIVITY_HOURS":
            return common_activity_hours(self.value, val)
        elif self.field_type == "NUMBER":
            return val >= self.value
        else:
            return val == self.value

    def __eq__(self, other):
        if isinstance(other, Question):
            if self.column_idx != other.column_idx:
                return False
            if self.field_type == "BOOL":
                return True
            elif self.field_type == "GEO_LOCATION":
                return is_closes_places(self.value, other.value, 0.1)
            elif self.field_type == "ACTIVITY_HOURS":
                return common_activity_hours(self.value, other.value, 0.9)
            else:
                return self.value == other.value

    def __repr__(self):
        # This is just a helper method to print
        # the question in a readable format.
        condition = "=="
        val_str = str(self.value)
        if self.field_type in ["GEO_LOCATION", "ACTIVITY_HOURS"]:
            condition = "∩"
        if self.field_type == "NUMBER":
            condition = ">="
            val_str = '{:.2f}'.format(self.value)
        return "%s %s %s" % (self.column, condition, val_str)


class Leaf:

    def __init__(self, value, size, mae):
        self.value = value
        self.size = size
        self.mae = mae

    def __str__(self) -> str:
        return "{:.2f} [{}] ({:.2f})".format(self.value, self.size, self.mae)


class DecisionNode:

    def __init__(self, question, true_branch, false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self) -> str:
        return str(self.question)
