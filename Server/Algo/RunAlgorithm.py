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
    id_experiments = ID3Experiments()
    id_experiments.basic_experiment()
