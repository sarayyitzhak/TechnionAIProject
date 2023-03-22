import math
import pandas as pd
from Server.DataBuilder.Utils import write_to_file

# pip install xlrd
# pip install openpyxl


def str_col_to_int(col):
    for i in range(len(col)):
        if col[i].isnumeric():
            col[i] = int(col[i])
    return col


def cbs_build_data():
    data = []
    cities = ['חיפה', 'טירת הכרמל', 'נשר', 'קריית אתא', 'קריית ביאליק', 'קריית ים', 'קריית מוצקין']
    religious_by_area = get_raw_data()

    for row in range(len(religious_by_area)):
        if religious_by_area.iloc[:, 0][row] in cities and isinstance(religious_by_area.iloc[:, 2][row], str):
            city = religious_by_area.iloc[:, 0][row]
            streets_list = religious_by_area.iloc[:, 2][row].split(', ')
            people_count = religious_by_area.iloc[:, 3][row]
            religions_count = religious_by_area.iloc[:, 4][row]
            if religions_count == '..':
                religions_count = 0

            for street in streets_list:
                exist = False
                for place in data:
                    if place["city"] == city and place["street"] == street:
                        exist = True
                        place["amount of people"] += people_count
                        place["amount of religious"] += religions_count
                        place["percent of religious"] += round((religions_count / people_count) * 100, 2)
                        break
                if not exist:
                    data.append({
                        "city": city,
                        "street": street,
                        "amount of people": people_count,
                        "amount of religious": religions_count,
                        "percent of religious": round((religions_count / people_count) * 100, 2)
                    })

    write_to_file(data, "./Dataset/cbs-data.json")


def get_raw_data():
    religious_by_key = pd.read_excel("./CbsInfo/religious_population.xlsx", sheet_name="חרדים במחוזות, ביישובים ובאס",
                                     engine='openpyxl', skiprows=9, usecols='B:G')
    transition_key = pd.read_excel("./CbsInfo/transition_area_key.xlsx", engine='openpyxl',
                                   usecols='B, C, E, G, H, J, K, M')
    area_by_key = pd.read_excel("./CbsInfo/streets_by_area_key.xlsx", engine='openpyxl', usecols='A:F')
    religious_by_key.reset_index(drop=True)
    transition_key.iloc[:, 2] = str_col_to_int(transition_key.iloc[:, 2])
    transition_key.iloc[:, 0] = str_col_to_int(transition_key.iloc[:, 0])
    religious_by_area_raw = religious_by_key.merge(transition_key, how='left',
                                                   left_on=[religious_by_key.keys()[0], religious_by_key.keys()[2]],
                                                   right_on=[transition_key.keys()[0], transition_key.keys()[2]])
    religious_by_area_raw = religious_by_area_raw.merge(area_by_key, how='left',
                                                        left_on=religious_by_area_raw.keys()[12],
                                                        right_on=area_by_key.keys()[1])

    return religious_by_area_raw.iloc[:, [14, 19, 18, 3, 4]].copy()


