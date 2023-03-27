import math
import pandas as pd
from Server.DataBuilder.Utils import write_to_file, write_dict_to_file

# pip install xlrd
# pip install openpyxl


def str_col_to_int(col):
    for i in range(len(col)):
        if col[i].isnumeric():
            col[i] = int(col[i])
    return col


def init_street_dict(area_by_key, cities, dict):
    for row in range(len(area_by_key)):
        if area_by_key.iloc[:, 0][row] in cities and isinstance(area_by_key.iloc[:, 1][row], str):
            city = area_by_key.iloc[:, 0][row]
            streets_list = area_by_key.iloc[:, 1][row].split(', ')
            streets_list = [street.replace("שד", "שדרות") for street in streets_list]
            for street in streets_list:
                # key_in_dict = (street, city) in dict
                key_in_dict = dict.get((street, city))
                if key_in_dict is None:
                    dict[(street, city)] = {
                        "amount of people": None,
                        "amount of religious": None,
                        "percent of religious": None,
                        "socio-economic index value": None,
                        "socio-economic rank": None,
                        "socio-economic cluster": None
                    }
    return dict


def cbs_build_data():
    cities = ['חיפה', 'טירת הכרמל', 'נשר', 'קריית אתא', 'קריית ביאליק', 'קריית ים', 'קריית מוצקין']
    data = {}
    religious_by_area, ser_by_area, area_by_key = get_raw_data()

    data = init_street_dict(area_by_key, cities, data)

    religious_by_street = []
    religious_by_area = religious_by_area[religious_by_area['רחובות עיקריים'].notna()].reset_index(drop=True)
    ser_by_area = ser_by_area[ser_by_area['רחובות עיקריים'].notna()].reset_index(drop=True)

    for row in range(len(religious_by_area)):
        if religious_by_area.iloc[:, 0][row] in cities and isinstance(religious_by_area.iloc[:, 2][row], str):
            city = religious_by_area.iloc[:, 0][row]
            streets_list = religious_by_area.iloc[:, 2][row].split(', ')
            streets_list = [street.replace("שד", "שדרות") for street in streets_list]
            people_count = religious_by_area.iloc[:, 3][row]
            religions_count = religious_by_area.iloc[:, 4][row]
            if religions_count == '..':
                religions_count = 0
            for street in streets_list:
                if data[(street, city)]["amount of people"] is None:
                    data[(street, city)]["amount of people"] = people_count
                    data[(street, city)]["amount of religious"] = religions_count
                    data[(street, city)]["percent of religious"] = round((religions_count / people_count) * 100, 2)
                else:
                    previous_data = data[(street, city)]
                    data[(street, city)]["amount of people"] = previous_data["amount of people"] + people_count
                    data[(street, city)]["amount of religious"] = previous_data["amount of religious"] + religions_count
                    data[(street, city)]["percent of religious"] = round((data[(street, city)]["amount of religious"] / data[(street, city)]["amount of people"]) * 100, 2)

    for row in range(len(ser_by_area)):
        if ser_by_area.iloc[:, 0][row] in cities and isinstance(ser_by_area.iloc[:, 4][row], str):
            city = ser_by_area.iloc[:, 0][row]
            streets_list = ser_by_area.iloc[:, 4][row].split(', ')
            streets_list = [street.replace("שד", "שדרות") for street in streets_list]
            index_value = ser_by_area.iloc[:, 1][row]
            rank = ser_by_area.iloc[:, 2][row]
            cluster = ser_by_area.iloc[:, 3][row]
            for street in streets_list:
                if data[(street, city)]["socio-economic index value"] is None:
                    data[(street, city)]["socio-economic index value"] = round(index_value, 3)
                    data[(street, city)]["socio-economic rank"] = rank
                    data[(street, city)]["socio-economic cluster"] = cluster
                else:
                    previous_data = data[(street, city)]
                    data[(street, city)]["socio-economic index value"] = round((previous_data["socio-economic index value"] + index_value) / 2, 3)
                    data[(street, city)]["socio-economic rank"] = (previous_data["socio-economic rank"] + rank) / 2
                    data[(street, city)]["socio-economic cluster"] = (previous_data["socio-economic cluster"] + cluster) / 2

    write_dict_to_file(data, "./Dataset/cbs-data.json")


def get_raw_data():
    religious_by_key = pd.read_excel("./CbsInfo/religious_population.xlsx", sheet_name="חרדים במחוזות, ביישובים ובאס",
                                     engine='openpyxl', skiprows=9, usecols='B:G')
    transition_key = pd.read_excel("./CbsInfo/transition_area_key.xlsx", engine='openpyxl',
                                    usecols='B, C, E, G, H, J, K, M')
    area_by_key = pd.read_excel("./CbsInfo/streets_by_area_key.xlsx", engine='openpyxl', usecols='A:F')
    ser_by_key = pd.read_excel("./CbsInfo/socio_economic_rank_2015.xls", usecols='A:C, E:G')

    ser_by_key.columns = ['סמל יישוב', 'שם יישוב', 'סמל א"ס', 'ערך מדד', 'דירוג', 'אשכול']
    religious_by_key.reset_index(drop=True)
    transition_key.iloc[:, 2] = str_col_to_int(transition_key.iloc[:, 2])
    transition_key.iloc[:, 0] = str_col_to_int(transition_key.iloc[:, 0])
    for row in range(len(area_by_key)):
        area_by_key.iloc[:, 0] = area_by_key.iloc[:, 0].replace(['קריית מוצקין', 'קריית ים', 'קריית אתא'],
                                                      ['קרית מוצקין', 'קרית ים', 'קרית אתא'])
        # if area_by_key.iloc[:, 0][row] in ["קריית אתא", "קריית ים", "קריית מוצקין"]:
        #     area_by_key.iloc[:, 0][row] = area_by_key.iloc[:, 0][row].replace("קריית", "קרית")


    religious_by_area_raw = religious_by_key.merge(transition_key, how='left',
                                                   left_on=[religious_by_key.keys()[0], religious_by_key.keys()[2]],
                                                   right_on=[transition_key.keys()[0], transition_key.keys()[2]])
    religious_by_area_raw = religious_by_area_raw.merge(area_by_key, how='left',
                                                        left_on=religious_by_area_raw.keys()[12],
                                                        right_on=area_by_key.keys()[1])

    ser_by_area_raw = ser_by_key.merge(transition_key, how='left', left_on= [ser_by_key.keys()[0], ser_by_key.keys()[2]], right_on=[transition_key.keys()[0], transition_key.keys()[2]])
    ser_by_area_raw = ser_by_area_raw.merge(area_by_key, how='left',
                                                        left_on=ser_by_area_raw.keys()[12],
                                                        right_on=area_by_key.keys()[1])
    x=12
    return religious_by_area_raw.iloc[:, [14, 19, 18, 3, 4, 12]].copy(), ser_by_area_raw.iloc[:, [14, 3, 4, 5, 18, 19, 12]].copy(), area_by_key.iloc[:, [0, 4]].copy()


