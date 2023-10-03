import pandas as pd
import numpy as np


def get_data(data_set_path, fields, target_field):
    data = pd.read_csv(data_set_path)
    field_names = [field["name"] for field in fields] + [target_field]
    data = data[field_names]

    for col in [field["name"] for field in fields if field["type"] == "GEO_LOCATION"]:
        data[col] = data[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

    return data
