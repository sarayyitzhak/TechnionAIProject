import json
import numpy as np
import pandas as pd


class FeatureSelectionAnalysis:

    # Should be called after parse data, but without clean_data
    @staticmethod
    def print_analysis():
        with open('./ConfigFiles/feature-selection-config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            fields = config["fields"]
            data = pd.read_csv(config["data_set_path"])
            field_names = [field["name"] for field in fields]
            data = data[field_names]

            for col in [field["name"] for field in fields if field["type"] == "GEO_LOCATION"]:
                data[col] = data[col].apply(lambda x: np.nan if pd.isnull(x) else tuple(eval(x)))

            for col in [field["name"] for field in config["fields"] if field["type"] == "GEO_LOCATION"]:
                data["latitude"] = data[col].apply(lambda x: np.nan if pd.isnull(x) else float(x[0]))
                data["longitude"] = data[col].apply(lambda x: np.nan if pd.isnull(x) else float(x[1]))

            for col in [field["name"] for field in config["fields"] if field["type"] == "BOOL"]:
                data[col] = data[col].apply(lambda x: np.nan if pd.isnull(x) else int(x))

            for col in [field["name"] for field in config["fields"] if field["type"] == "STRING"]:
                data[col] = data[col].astype('category').cat.codes
                data[col] = data[col].apply(lambda x: np.nan if x == -1 else x)

            print(data.corr().to_string())
