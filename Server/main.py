from Server.DataParser.DataParser import *
from Server.DataBuilder.CbsDataBuilder import *
from Server.DataBuilder.GovDataBuilder import *
from Server.Algo.ID3 import *
from Server.Algo.ID3Experiments import *
import pandas as pd
import urllib.request
import json
import math
import textdistance

def main():
    # unneeded_labels = ["name", "user_ratings_total", "Unnamed: 0", "vicinity", "street", "city"]
    # attributes_names = list(pd.read_csv("./Dataset/data.csv", delimiter=",", dtype=str, nrows=1).keys())
    # for label in unneeded_labels:
    #     attributes_names.remove(label)
    # train_set = pd.read_csv("./Dataset/data.csv")
    # train_set.drop(unneeded_labels, axis='columns', inplace=True)
    # x_train = np.array(train_set.drop('rating', axis=1).copy())
    # y_train = np.array(train_set['rating'].copy())
    # id3 = ID3(attributes_names, 500)
    # id3.fit(x_train, y_train)
    id_experiments = ID3Experiments()
    id_experiments.basic_experiment()
    # cbs_build_data()
    # parse_data()


if __name__ == '__main__':
    start = time.time()
    main()
    print("TOTAL TIME: " + str(time.time() - start) + " seconds")
