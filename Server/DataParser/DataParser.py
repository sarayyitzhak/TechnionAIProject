import math
import pandas as pd
import numpy as np
import textdistance
import time
import mpu

cities_list = ['חיפה', 'טירת הכרמל', 'נשר', 'קריית אתא', 'קריית ביאליק', 'קריית ים', 'קריית מוצקין']


def parse_bool_col(col, df):
    values = []
    for row in range(len(df)):
        if df[col][row] == 0.0:
            values.append(False)
        elif df[col][row] == 1.0:
            values.append(True)
        else:
            values.append(None)
    return values


def parse_open_hours(row, col, df):
    open_hours = {}
    start_hour = "0000"
    end_hour = "2400"
    for day in range(7):
        open_hours[day] = []
    if type(df[col][row]) is dict:
        periods = df[col][row]['periods']
        if 'close' not in periods[0]:
            for day in range(7):
                time = {'open': start_hour, 'close': end_hour}
                open_hours[day].append(time)
        else:
            for i in range(len(periods)):
                if periods[i]['open']['time'] < periods[i]['close']['time']:
                    time = {'open': periods[i]['open']['time'], 'close': periods[i]['close']['time']}
                else:
                    time = {'open': periods[i]['open']['time'], 'close': end_hour}
                    if periods[i]['close']['time'] != start_hour:
                        time_after_midnight = {'open': start_hour, 'close': periods[i]['close']['time']}
                        open_hours[(periods[i]['open']['day'] + 1) % 7].append(time_after_midnight)
                open_hours[periods[i]['open']['day']].append(time)
    return open_hours


def get_address(df, row):
    col = "address_components"
    name_type = "long_name"
    city, street, street_reversed = None, None, None
    for component in df[col][row]:
        if "locality" in component["types"]:
            city = component[name_type]
        if "route" in component["types"]:
            street = component[name_type]
            street_reversed = " ".join(street.split(" ")[::-1])
    return city, street, street_reversed


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
                            data = cbs_data[cbs_key]

        if data is not None:
            religious_percent = data["percent of religious"]
            se_index = data["socio-economic index value"]
            se_rank = data["socio-economic rank"]
            se_cluster = data["socio-economic cluster"]
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
        city, street, street_reversed = get_address(google_df, row)
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
        if type(google_df['reviews'][row]) == float and math.isnan(google_df['reviews'][row]):
            reviews_words = None
        else:
            for review in google_df['reviews'][row]:
                r_text = review['text']
                clean_r_text = r_text.replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\n', ' ').replace('?', ' ')
                reviews_words.update(clean_r_text.split(' '))
        reviews.append(reviews_words)
    return reviews


def distance(s1, s2):
    if not s1 and not s2:
        return 0
    return textdistance.strcmp95.normalized_similarity(s1, s2)


def copy_column(col, df):
    values = []
    for row in range(len(df)):
        values.append(df[col][row])
    return values


def parse_data():
    google_df = pd.read_json("./Dataset/google-data.json")
    google_places_df = pd.read_json("./Dataset/google-places-data.json")
    rest_df = pd.read_json("./Dataset/rest-data.json")
    cbs_df = pd.read_json("./Dataset/cbs-data.json")
    gov_df = pd.read_json("./Dataset/gov-data.json")
    result = {}

    google_df = google_df[google_df['rating'].notna()].reset_index(drop=True)

    for col in ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout', 'wheelchair_accessible_entrance', 'curbside_pickup']:
        result[col] = parse_bool_col(col, google_df)

    result['website'] = [type(google_df['website'][row]) == str for row in range(len(google_df))]

    for col in ['name', 'vicinity']:
        result[col] = copy_column(col, google_df)

    result['city'], result['street'], result['religious_percent'], result['socio-economic_index_value'], result['socio-economic_rank'], result['socio-economic_cluster'] = parse_cbs(google_df, cbs_df)

    for col in ['sunday_open_hours', 'monday_open_hours', 'tuesday_open_hours', 'wednesday_open_hours', 'thursday_open_hours', 'friday_open_hours', 'saturday_open_hours']:
        result[col] = []
    col = 'opening_hours'
    for row in range(len(google_df)):
        open_hours = parse_open_hours(row, col, google_df)
        result['sunday_open_hours'].append(open_hours[0])
        result['monday_open_hours'].append(open_hours[1])
        result['tuesday_open_hours'].append(open_hours[2])
        result['wednesday_open_hours'].append(open_hours[3])
        result['thursday_open_hours'].append(open_hours[4])
        result['friday_open_hours'].append(open_hours[5])
        result['saturday_open_hours'].append(open_hours[6])

    result['reviews_words'] = parse_reviews(google_df)

    for col in ['price_level', 'rating', 'user_ratings_total']:
        result[col] = copy_column(col, google_df)

    store_100_values = []
    store_500_values = []
    rest_100_values = []
    rest_500_values = []
    for row in range(len(google_df)):
        store_100_count = 0
        store_500_count = 0
        rest_100_count = 0
        rest_500_count = 0
        g_point_lat_lng = google_df["geometry"][row]["location"]
        g_point = (g_point_lat_lng["lat"], g_point_lat_lng["lng"])
        for place_row in range(len(google_places_df)):
            if google_places_df["place_id"][place_row] == google_df["place_id"][row]:
                continue
            place_point_lat_lng = google_places_df["geo_location"][place_row]
            place_point = (place_point_lat_lng["lat"], place_point_lat_lng["lng"])
            point_distance = mpu.haversine_distance(g_point, place_point)
            if point_distance < 0.5:
                if google_places_df["type"][place_row] == "store":
                    store_500_count += 1
                    if point_distance < 0.1:
                        store_100_count += 1
                else:
                    rest_500_count += 1
                    if point_distance < 0.1:
                        rest_100_count += 1
        store_100_values.append(store_100_count)
        store_500_values.append(store_500_count)
        rest_100_values.append(rest_100_count)
        rest_500_values.append(rest_500_count)

    result["store_100"] = store_100_values
    result["store_500"] = store_500_values
    result["rest_100"] = rest_100_values
    result["rest_500"] = rest_500_values

    bus_station_100_values = []
    bus_station_500_values = []
    for row in range(len(google_df)):
        bus_station_100_count = 0
        bus_station_500_count = 0
        g_point_lat_lng = google_df["geometry"][row]["location"]
        g_point = (g_point_lat_lng["lat"], g_point_lat_lng["lng"])
        for place_row in range(len(gov_df)):
            place_point_lat_lng = gov_df["geo_location"][place_row]
            place_point = (place_point_lat_lng["lat"], place_point_lat_lng["lng"])
            point_distance = mpu.haversine_distance(g_point, place_point)
            if point_distance < 0.5:
                bus_station_500_count += 1
                if point_distance < 0.1:
                    bus_station_100_count += 1
        bus_station_100_values.append(bus_station_100_count)
        bus_station_500_values.append(bus_station_500_count)

    result["bus_station_100"] = bus_station_100_values
    result["bus_station_500"] = bus_station_500_values

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

    rest_values = rest_df.values.copy()

    type_values = []
    kosher_values = []
    for row in range(len(google_df)):
        g_name = google_df["name"][row]
        g_address = google_df["vicinity"][row]
        g_city = None
        for address_component in google_df["address_components"][row]:
            if "locality" in address_component["types"]:
                g_city = address_component["long_name"]
        g_name_strong = " ".join([item for item in g_name.split(" ") if item not in common_words_strong])
        g_name_weak = " ".join([item for item in g_name.split(" ") if item not in common_words_weak])
        first_best_dist = 0.9
        second_best_dist = 0.8
        third_best_dist = 0
        first_best_value = None
        second_best_value = None
        third_best_value = None
        for value in rest_values:
            if g_city != value[4]:
                continue
            r_name_strong = " ".join([item for item in value[1].split(" ") if item not in common_words_strong])
            name_dist = distance(g_name_strong, r_name_strong)
            if name_dist > first_best_dist:
                first_best_dist = name_dist
                first_best_value = value

            if first_best_value is None:
                place_dist = distance(value[5], g_address.split(" ")[0])
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
    frame.to_csv("./Dataset/data.csv")



