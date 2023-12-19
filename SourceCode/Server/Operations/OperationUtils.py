import pandas as pd
import numpy as np

from SourceCode.Server.Utils.Utils import is_closes_places


def get_same_type_count(data_set_path, user_data):
    data = pd.read_csv(data_set_path)
    data["geo_location"] = data["geo_location"].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

    count = 0
    for row in range(len(data)):
        is_close = is_closes_places(data["geo_location"][row], user_data["geo_location"], 1)
        is_same_type = data["type"][row] == user_data["type"]
        if is_close and is_same_type:
            count += 1

    return count


def get_rate_position(data_set_path, user_grade, user_geo_location):
    data = pd.read_csv(data_set_path)
    data["geo_location"] = data["geo_location"].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

    count = 1
    position = 1
    for row in range(len(data)):
        is_close = is_closes_places(data["geo_location"][row], user_geo_location, 1)
        if is_close:
            count += 1
            if data["grade"][row] > user_grade:
                position += 1

    return count, position


def get_data(data_set_path, fields, target_field):
    data = pd.read_csv(data_set_path)
    field_names = [field["name"] for field in fields] + [target_field]
    data = data[field_names]

    for col in [field["name"] for field in fields if field["type"] == "GEO_LOCATION"]:
        data[col] = data[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

    return data
