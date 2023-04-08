import math
import pandas as pd
import numpy as np
import textdistance
import time
import mpu

cities_list = ['חיפה', 'טירת הכרמל', 'נשר', 'קריית אתא', 'קריית ביאליק', 'קריית ים', 'קריית מוצקין']


def parse_bool_col(df, col):
    return [None if math.isnan(df[col][row]) else bool(df[col][row]) for row in range(len(df))]


def parse_not_none_col(df, col):
    return [df[col][row] is not None for row in range(len(df))]


def copy_column(df, col):
    return [df[col][row] for row in range(len(df))]


def get_cbs_data(cbs_data: dict, city, street, street_reversed):
    religious_percent, se_index, se_rank, se_cluster = None, None, None, None
    if city is not None and street is not None:
        key = (street, city)
        reversed_key = (street_reversed, city)
        data = cbs_data.get(key)
        if data is None:
            data = cbs_data.get(reversed_key)
            if data is None:
                for cbs_key in cbs_data.keys():
                    if cbs_key[1] == city:
                        if max(textdistance.strcmp95(cbs_key[0], street), textdistance.strcmp95(cbs_key[0], street_reversed)) > 0.9:
                            data = cbs_data.get(cbs_key)

        if data is not None:
            religious_percent = None if math.isnan(data["percent of religious"]) else data["percent of religious"]
            se_index = None if math.isnan(data["socio-economic index value"]) else data["socio-economic index value"]
            se_rank = None if math.isnan(data["socio-economic rank"]) else data["socio-economic rank"]
            se_cluster = None if math.isnan(data["socio-economic cluster"]) else data["socio-economic cluster"]
    return religious_percent, se_index, se_rank, se_cluster


def parse_cbs(google_df, cbs_df):
    cities, streets, religious, se_index_values, se_ranks, se_clusters = [], [], [], [], [], []
    cbs_data = {}

    for row in range(len(cbs_df)):
        key = (cbs_df["street"][row], cbs_df["city"][row])
        cbs_data[key] = {
            "percent of religious": cbs_df["percent of religious"][row],
            "socio-economic index value": cbs_df["socio-economic index value"][row],
            "socio-economic rank": cbs_df["socio-economic rank"][row],
            "socio-economic cluster": cbs_df["socio-economic cluster"][row]
        }

    for row in range(len(google_df)):
        city = google_df["address"][row]["city"]
        street = google_df["address"][row]["street"]
        street_reversed = None if street is None else " ".join(street.split(" ")[::-1])
        religious_percent, se_index, se_rank, se_cluster = get_cbs_data(cbs_data, city, street, street_reversed)
        religious.append(religious_percent)
        se_index_values.append(se_index)
        se_ranks.append(se_rank)
        se_clusters.append(se_cluster)
        cities.append(city)
        streets.append(street)
    return cities, streets, religious, se_index_values, se_ranks, se_clusters


def parse_reviews(google_df):
    reviews = []
    for row in range(len(google_df)):
        reviews_words = set()
        for review in google_df['reviews'][row]:
            clean_r_text = review.replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\n', ' ').replace('?', ' ')
            reviews_words.update(clean_r_text.split(' '))
        reviews.append(reviews_words)
    return reviews


def get_near_by_places(point, df):
    place_500_count = 0
    place_100_count = 0
    for row in range(len(df)):
        place_point_lat_lng = df["geo_location"][row]
        place_point = (place_point_lat_lng["lat"], place_point_lat_lng["lng"])
        point_distance = mpu.haversine_distance(point, place_point)
        if point_distance < 0.5:
            place_500_count += 1
            if point_distance < 0.1:
                place_100_count += 1
    return place_500_count, place_100_count


def fill_missing_data_by_nearby_streets(result, col_name):
    blank_rows, full_rows = {}, {}
    blank, idx_blank, full, place_lng_blank = [], [], [], []
    place_lat_blank, place_lng_full, place_lat_full = [], [], []
    for idx, val in enumerate(result[col_name]):
        if val is None:
            blank.append(val)
            idx_blank.append(idx)
            place_lng_blank.append(result["lng"][idx])
            place_lat_blank.append(result["lat"][idx])
        else:
            full.append(val)
            place_lng_full.append(result["lng"][idx])
            place_lat_full.append(result["lat"][idx])

    blank_rows["value"] = blank
    blank_rows["idx"] = idx_blank
    blank_rows["sum"] = [None] * len(blank_rows["value"])
    blank_rows["num"] = [None] * len(blank_rows["value"])
    blank_rows["lng"] = place_lng_blank
    blank_rows["lat"] = place_lat_blank
    full_rows["value"] = full
    full_rows["lng"] = place_lng_full
    full_rows["lat"] = place_lat_full
    for blank_row in range(len(blank_rows["value"])):
        blank_point = (blank_rows["lat"][blank_row], blank_rows["lng"][blank_row])
        for full_row in range(len(full_rows["value"])):
            full_point = (full_rows["lat"][full_row], full_rows["lng"][full_row])
            point_distance = mpu.haversine_distance(blank_point, full_point)
            if point_distance < 0.5:
                if blank_rows["sum"][blank_row] is None:
                    blank_rows["sum"][blank_row] = 0
                    blank_rows["num"][blank_row] = 0
                blank_rows["sum"][blank_row] += full_rows["value"][full_row]
                blank_rows["num"][blank_row] += 1
        if blank_rows["sum"][blank_row] is not None:
            result[col_name][blank_rows["idx"][blank_row]] = round(blank_rows["sum"][blank_row] / blank_rows["num"][blank_row], 3)


def cbs_fill_missing_data(result):
    for col in ["religious_percent", "socio-economic_index_value", "socio-economic_rank", "socio-economic_cluster"]:
        fill_missing_data_by_nearby_streets(result, col)


def distance(s1, s2):
    if not s1 and not s2:
        return 0
    return textdistance.strcmp95.normalized_similarity(s1, s2)


def parse_data():
    google_df = pd.read_json("./Dataset/google-data.json")
    google_places_df = pd.read_json("./Dataset/google-places-data.json")
    rest_df = pd.read_json("./Dataset/rest-data.json")
    cbs_df = pd.read_json("./Dataset/cbs-data.json")
    gov_df = pd.read_json("./Dataset/gov-data.json")
    result = {}

    google_df = google_df[google_df['rating'].notna()].reset_index(drop=True)

    bool_cols = ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch',
                 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout',
                 'wheelchair_accessible_entrance', 'curbside_pickup']
    copy_cols = ["name", 'price_level', 'rating', 'user_ratings_total', "sunday_activity_hours", "monday_activity_hours", "tuesday_activity_hours",
                 "wednesday_activity_hours", "thursday_activity_hours", "friday_activity_hours",
                 "saturday_activity_hours"]

    for col in bool_cols:
        result[col] = parse_bool_col(google_df, col)

    result["website"] = parse_not_none_col(google_df, "website")

    for col in copy_cols:
        result[col] = copy_column(google_df, col)

    result['reviews_words'] = parse_reviews(google_df)

    result['city'], result['street'], result['religious_percent'], result['socio-economic_index_value'], result['socio-economic_rank'], result['socio-economic_cluster'] = parse_cbs(google_df, cbs_df)

    rest_places_df = google_places_df.loc[google_places_df['type'] == "restaurant"].reset_index(drop=True)
    store_places_df = google_places_df.loc[google_places_df['type'] == "store"].reset_index(drop=True)
    result["store_100"] = []
    result["store_500"] = []
    result["rest_100"] = []
    result["rest_500"] = []
    result["bus_station_100"] = []
    result["bus_station_500"] = []
    for row in range(len(google_df)):
        g_point_lat_lng = google_df["address"][row]["geo_location"]
        g_point = (g_point_lat_lng["lat"], g_point_lat_lng["lng"])
        rest_places_except_this_df = rest_places_df.loc[rest_places_df['place_id'] != google_df["place_id"][row]].reset_index(drop=True)
        rest_500_count, rest_100_count = get_near_by_places(g_point, rest_places_except_this_df)
        store_500_count, store_100_count = get_near_by_places(g_point, store_places_df)
        bus_station_500_count, bus_station_100_count = get_near_by_places(g_point, gov_df)
        result["store_500"].append(store_500_count)
        result["store_100"].append(store_100_count)
        result["rest_500"].append(rest_500_count)
        result["rest_100"].append(rest_100_count)
        result["bus_station_500"].append(bus_station_500_count)
        result["bus_station_100"].append(bus_station_100_count)


    result["lat"] = []
    result["lng"] = []
    for row in range(len(google_df)):
        g_point_lat_lng = google_df["address"][row]["geo_location"]
        result["lat"].append(g_point_lat_lng["lat"])
        result["lng"].append(g_point_lat_lng["lng"])

    cbs_fill_missing_data(result)

    common_words = {}
    for r_name in rest_df['name']:
        for word in set(r_name.split(" ")):
            if word not in common_words:
                common_words[word.lower()] = 0
            common_words[word.lower()] += 1

    for row in range(len(google_df)):
        g_name = google_df["name"][row]
        for word in set(g_name.split(" ")):
            if word not in common_words:
                common_words[word.lower()] = 0
            common_words[word.lower()] += 1

    common_words_strong = [key for key, value in common_words.items() if value >= 15]
    common_words_weak = [key for key, value in common_words.items() if value >= 5]

    rest_by_city = {}
    for value in rest_df.values:
        if value[4] not in rest_by_city:
            rest_by_city[value[4]] = []
        rest_by_city[value[4]].append(value)

    type_values = []
    kosher_values = []
    for row in range(len(google_df)):
        g_name = google_df["name"][row]
        g_address = google_df["address"][row]
        g_vicinity = (g_address["street"] or '') + " " + (g_address["street_number"] or '')
        g_city = g_address["city"]
        g_name_strong = " ".join([item for item in g_name.split(" ") if item not in common_words_strong])
        g_name_weak = " ".join([item for item in g_name.split(" ") if item not in common_words_weak])
        first_best_dist = 0.9
        second_best_dist = 0.8
        third_best_dist = 0
        first_best_value = None
        second_best_value = None
        third_best_value = None
        if g_city in rest_by_city:
            for value in rest_by_city[g_city]:
                r_name_strong = " ".join([item for item in value[1].split(" ") if item not in common_words_strong])
                name_dist = distance(g_name_strong, r_name_strong)
                if name_dist > first_best_dist:
                    first_best_dist = name_dist
                    first_best_value = value

                if first_best_value is None:
                    place_dist = distance(value[5], g_vicinity)
                    if place_dist > 0.85 and name_dist > second_best_dist:
                        second_best_dist = name_dist
                        second_best_value = value

                    if second_best_value is None:
                        r_name_weak = " ".join([item for item in value[1].split(" ") if item not in common_words_weak])
                        common_words = len(list(set(g_name_weak.lower().split(" ")) & set(r_name_weak.lower().split(" "))))
                        if distance(g_name_weak, r_name_weak) > 0.8 and common_words > third_best_dist:
                            third_best_dist = common_words
                            third_best_value = value

        if first_best_value is not None:
            type_values.append(first_best_value[2])
            kosher_values.append(first_best_value[3])
        elif second_best_value is not None:
            type_values.append(second_best_value[2])
            kosher_values.append(second_best_value[3])
        elif third_best_value is not None:
            type_values.append(third_best_value[2])
            kosher_values.append(third_best_value[3])
        else:
            type_values.append(None)
            kosher_values.append(None)

    result["kosher"] = kosher_values
    result["type"] = type_values

    frame = pd.DataFrame(result)
    frame.to_csv("./Dataset/data.csv", index=False, encoding='utf-8-sig')



