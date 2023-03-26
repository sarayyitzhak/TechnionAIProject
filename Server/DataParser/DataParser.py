import numbers
import math
import pandas as pd
import textdistance

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
    for day in range(7):
        open_hours[day] = []
    if type(df[col][row]) is dict:
        periods = df[col][row]['periods']
        if 'close' not in periods[0]:
            for day in range(7):
                time = {'open': '0000', 'close': '2400'}
                open_hours[day].append(time)
        else:
            for i in range(len(periods)):
                if periods[i]['open']['time'] < periods[i]['close']['time']:
                    time = {'open': periods[i]['open']['time'], 'close': periods[i]['close']['time']}
                else:
                    time = {'open': periods[i]['open']['time'], 'close': '2400'}
                    if periods[i]['close']['time'] != '0000':
                        time_after_midnight = {'open': '0000', 'close': periods[i]['close']['time']}
                        open_hours[(periods[i]['open']['day'] + 1) % 7].append(time_after_midnight)
                open_hours[periods[i]['open']['day']].append(time)
    return open_hours


def parse_religious(col, google_df, cbs_df):
    cities = []
    streets = []
    religious =[]
    for row in range(len(google_df)):
        if ',' in google_df[col][row]:
            address = google_df[col][row].split(", ")
            city = address.pop(len(address) - 1)
            street = "".join(address) if len(address) == 1 else " ".join(address)
            cities.append(city)
            streets.append(street)
            religious1 = -1
            for row1 in range(len(cbs_df)):
                if cbs_df.iloc[row1]['city'] in city and (cbs_df.iloc[row1]['street'] in street or cbs_df.iloc[row1]['street'] in " ".join(street.split(" ")[::-1])):
                    religious1 = cbs_df.iloc[row1]['percent of religious']
                    break
            religious.append(religious1) if religious1 > -1 else religious.append(None)
        else:
            cities.append(google_df[col][row]) if google_df[col][row] in cities_list else cities.append(None)
            streets.append(None)
            religious.append(None)
    return cities, streets, religious


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


def parse_data():
    google_df = pd.read_json("./Dataset/google-data.json")
    rest_df = pd.read_json("./Dataset/rest-data.json")
    cbs_df = pd.read_json("./Dataset/cbs-data.json")
    result = {}

    google_df = google_df[google_df['rating'].notna()].reset_index(drop=True)

    for col in ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout', 'wheelchair_accessible_entrance', 'curbside_pickup']:
        result[col] = parse_bool_col(col, google_df)

    result['website'] = [type(google_df['website'][row]) == str for row in range(len(google_df))]

    for col in ['name', 'vicinity']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

    col = 'vicinity'
    result['city'], result['street'], result['religious'] = parse_religious(col, google_df, cbs_df)

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
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

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



