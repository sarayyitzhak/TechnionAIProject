import numbers
import math
import pandas as pd

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


def parse_data():
    google_df = pd.read_json("./Dataset/google-data.json")
    cbs_df = pd.read_json("./Dataset/cbs-data.json")
    result = {}

    for col in ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout', 'wheelchair_accessible_entrance', 'curbside_pickup']:
        result[col] = parse_bool_col(col, google_df)

    result['website'] = [type(google_df['website'][row]) == str for row in range(len(google_df))]

    for col in ['name', 'vicinity']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

    col = 'vicinity'
    cities = []
    streets = []
    religious =[]

    for row in range(len(google_df)):
        if ',' in google_df[col][row]:
            address = google_df[col][row].split(", ")
            city = address.pop(len(address) - 1)
            street = "".join(address) if len(address) == 1 else " ".join(address)
            # streets.append(*address) if len(address) == 1 else streets.append(" ".join(address))
            cities.append(city)
            streets.append(street)
            religious1 = -1
            for row1 in range(len(cbs_df)):
                if cbs_df.iloc[row1]['city'] in city and cbs_df.iloc[row1]['street'] in street:
                    religious1 = cbs_df.iloc[row1]['percent of religious']
                    break
            religious.append(religious1) if religious1 > -1 else religious.append(None)
        else:
            cities.append(google_df[col][row]) if google_df[col][row] in cities_list else cities.append(None)
            streets.append(None)
            religious.append(None)
    result['city'] = cities
    result['street'] = streets
    result['religious'] = religious

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
    result['reviews_words'] = reviews

    for col in ['price_level', 'rating', 'user_ratings_total']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

    for row in range(len(google_df)):
        if row > len(result):
            break
        if math.isnan(google_df['rating'][row]):
            for col in result:
                result[col].pop(row)

    pd.DataFrame(result).to_csv("./Dataset/data.csv")



