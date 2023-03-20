import numbers
import math
import pandas as pd


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
        open_hours[day] = None
    if type(df[col][row]) is dict:
        periods = df[col][row]['periods']
        for i in range(len(periods)):
            if periods[i]['open']['time'] < periods[i]['close']['time']:
                time = {'open': periods[i]['open']['time'], 'close': periods[i]['close']['time']}
            else:
                time = {'open': periods[i]['open']['time'], 'close': '2400'}
                if periods[i]['close']['time'] != '0000':
                    time_after_midnight = {'open': '0000', 'close': periods[i]['close']['time']}
                    if open_hours[(periods[i]['open']['day'] + 1) % 7] is None:
                        open_hours[(periods[i]['open']['day'] + 1) % 7] = []
                    open_hours[(periods[i]['open']['day'] + 1) % 7].append(time_after_midnight)
            if open_hours[periods[i]['open']['day']] is None:
                open_hours[periods[i]['open']['day']] = []
            open_hours[periods[i]['open']['day']].append(time)
    return open_hours


def parse_data():
    google_df = pd.read_json("../Dataset/google-data.json")
    result = {}

    for col in ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout', 'wheelchair_accessible_entrance', 'curbside_pickup']:
        result[col] = parse_bool_col(col, google_df)

    result['website'] = [type(google_df['website'][row]) == str for row in range(len(google_df))]

    for col in ['name', 'vicinity']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

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

    for col in ['price_level', 'rating', 'user_ratings_total']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

    reviews = []
    for row in range(len(google_df)):
        reviews_words = set()
        for review in google_df['reviews'][row]:
            r_text = review['text']
            clean_r_text = r_text.replace('!', ' ').replace('.', ' ').replace(',', ' ').replace('\n', ' ').replace('?', ' ')
            reviews_words.update(clean_r_text.split(' '))
        reviews.append(reviews_words)
    result['reviews_words'] = reviews

    for row in range(len(google_df)):
        if math.isnan(google_df['rating'][row]):
            for col in result:
                result[col].pop(row)

    pd.DataFrame(result).to_csv("../Dataset/data.csv")



