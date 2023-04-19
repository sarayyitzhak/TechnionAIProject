import pandas as pd
from Server.DataParser.DataParser import *
from Server.DataBuilder.CbsDataBuilder import *
from Server.DataBuilder.GovDataBuilder import *
from Server.Algo.ID3 import *
from Server.Algo.ID3Experiments import *
import urllib.request
import json
import math
import textdistance


def run_alg():
    unneeded_labels = ["name", "user_ratings_total", "Unnamed: 0", "vicinity", "street", "city"]
    attributes_names = list(pd.read_csv("../server/Dataset/data.csv", delimiter=",", dtype=str, nrows=1).keys())
    for label in unneeded_labels:
        attributes_names.remove(label)
    train_set = pd.read_csv("..server/Dataset/data.csv")
    train_set.drop(unneeded_labels, axis='columns', inplace=True)
    x_train = np.array(train_set.drop('rating', axis=1).copy())
    y_train = np.array(train_set['rating'].copy())
    id3 = ID3(attributes_names, 500)
    id3.fit(x_train, y_train)
    id_experiments = ID3Experiments()
    id_experiments.basic_experiment()
    return id3