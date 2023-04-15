import numbers
import numpy as np
import mpu


def is_closes_places(value1, value2):
    return location_distance(value1, value2) < 0.3


def common_activity_hours(value1, value2):
    if len(value1) == len(value2) == 0 or value1 == (-1, -1) or value2 == (-1, -1):
        return True
    elif len(value1) != len(value2):
        return False
    else:
        total_minutes = (value1[1] - value1[0]) + (value2[1] - value2[0])
        intersection_total_minutes = get_intersection_total_minutes(value1, value2)

        common = (intersection_total_minutes * 2) / total_minutes
        return common > 0.8


def get_intersection_total_minutes(interval1, interval2):
    new_min = max(interval1[0], interval2[0])
    new_max = min(interval1[1], interval2[1])
    return new_max - new_min if new_min <= new_max else 0


def common_reviews(review1, review2):
    common = 0
    words = []
    for word in review1:
        if word in review2:
            common += 1
            words.append(word)
    return common, words


def location_distance(p1, p2):
    return mpu.haversine_distance(p1, p2)


def is_numeric(value):
    if type(value) is bool:
        return False
    return isinstance(value, numbers.Number)


def unique_vals(rows, col):
    return set([row[col] for row in rows])


class Question:

    def __init__(self, column, column_idx, value, var = 0):
        self.column = column
        self.column_idx = column_idx
        self.value = value
        self.var = var

    def match(self, example):
        # Compare the feature value in an example to the
        # feature value in this question.
        val = example[self.column_idx]
        if self.column == "geo_location":
            return is_closes_places(self.value, val)
        elif type(val) == tuple:
            # case of open hours
            return common_activity_hours(self.value, val)
        elif is_numeric(val):
            return val >= self.value
        else:
            return val == self.value

    def __repr__(self):
        # This is just a helper method to print
        # the question in a readable format.
        condition = "=="
        val_str = str(self.value)
        if type(self.value) == tuple:
            condition = "∩"
        if is_numeric(self.value):
            condition = ">="
            val_str = '{:.2f}'.format(self.value)
        return "%s %s %s" % (self.column, condition, val_str)


class Leaf:

    def __init__(self, labels):
        self.size = len(labels)
        self.mean = np.mean(labels)
        self.mse = np.mean((labels - self.mean) ** 2)

    def __str__(self) -> str:
        return "{:.2f} [{}] ({:.2f})".format(self.mean, self.size, self.mse)


class DecisionNode:

    def __init__(self,
                 question,
                 true_branch,
                 false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __str__(self) -> str:
        return str(self.question)
