from Server.Algo.ID3 import *
import pandas as pd


class ID3Experiments:

    def __init__(self):
        pass

    def basic_experiment(self):
        unneeded_labels = ["name", "user_ratings_total", "sunday_activity_hours", "monday_activity_hours",
                           "tuesday_activity_hours", "wednesday_activity_hours", "thursday_activity_hours",
                           "friday_activity_hours", "saturday_activity_hours", "reviews_words"]
        attributes_names = list(pd.read_csv("./Dataset/data.csv", delimiter=",", dtype=str, nrows=1).keys())
        for label in unneeded_labels:
            attributes_names.remove(label)
        train_set = pd.read_csv("./Dataset/data.csv")
        train_set = train_set.where(pd.notnull(train_set), None)
        train_set.drop(unneeded_labels, axis='columns', inplace=True)
        x_train = np.array(train_set.drop('rating', axis=1).copy())
        y_train = np.array(train_set['rating'].copy())
        id3 = ID3(attributes_names, 500)
        id3.fit(x_train, y_train)
