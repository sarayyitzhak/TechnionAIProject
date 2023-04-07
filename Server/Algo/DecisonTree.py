import numbers


def are_hours_contained(value1, value2):
    # check if value2 is contained in value1
    is_contained = False
    are_all_contained = True
    for i in value2:
        for j in value1:
            is_contained = is_contained or value2[i]['open'] >= value1[j]['open'] and value2[i]['close'] <= value1[j]['close']
        are_all_contained = are_all_contained and is_contained
    return are_all_contained


def common_reviews(review1, review2):
    common = 0
    words = []
    for word in review1:
        if word in review2:
            common += 1
            words.append(word)
    return common, words


def class_counts(rows, labels):
    counts = {cls: 0 for cls in set(labels)}  # a dictionary of label -> count.
    for idx, x in enumerate(rows):
        # in our dataset format, the label is always the last column
        label = labels[idx]
        counts[label] += 1
    return counts


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
        if type(val) == list:
            if self.column_idx in range(16, 23):
                # case of open hours
                return are_hours_contained(self.value, val)
        elif is_numeric(val):
            return val >= self.value
        else:
            return val == self.value

    def __repr__(self):
        # This is just a helper method to print
        # the question in a readable format.
        condition = "=="
        val_str = str(self.value)
        if is_numeric(self.value):
            condition = ">="
            val_str = '{:.2f}'.format(self.value)
        return "%s  %s" % (self.column, val_str)


class Leaf:

    def __init__(self, rows, labels):
        self.predictions = class_counts(rows, labels)

    def __str__(self) -> str:
        pred = self.predictions
        pred_str = ''.join(f'{c} : {pred[c]} \n' for c in pred.keys())
        return pred_str


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
