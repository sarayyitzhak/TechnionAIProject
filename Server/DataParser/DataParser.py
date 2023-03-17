import numbers
import math
import pandas as pd


def parse_data():
    google_df = pd.read_json("../Dataset/google-data.json")
    result = {}

    for col in ['dine_in', 'delivery', 'reservable', 'serves_beer', 'serves_breakfast', 'serves_brunch', 'serves_dinner', 'serves_lunch', 'serves_vegetarian_food', 'serves_wine', 'takeout', 'wheelchair_accessible_entrance', 'curbside_pickup']:
        values = []
        for row in range(len(google_df)):
            if google_df[col][row] == 0.0:
                values.append(True)
            elif google_df[col][row] == 1.0:
                values.append(False)
            else:
                values.append(None)
        result[col] = values

    for col in ['name', 'vicinity']:
        values = []
        for row in range(len(google_df)):
            values.append(google_df[col][row])
        result[col] = values

    result['website'] = [type(google_df['website'][row]) == str for row in range(len(google_df))]

    for col in ['sunday_open_hours', 'monday_open_hours', 'tuesday_open_hours', 'wednesday_open_hours', 'thursday_open_hours', 'friday_open_hours', 'saturday_open_hours']:
        result[col] = []
    col = 'opening_hours'
    for row in range(len(google_df)):
        open_hours = {}
        for day in range(7):
            open_hours[day] = None
        if type(google_df[col][row]) is dict:
            periods = google_df[col][row]['periods']
            for i in range(len(periods)):
                time = {'open': periods[i]['open']['time'], 'close': periods[i]['close']['time']}
                if open_hours[periods[i]['open']['day']] is None:
                    open_hours[periods[i]['open']['day']] = []
                open_hours[periods[i]['open']['day']].append(time)
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

    for row in range(len(google_df)):
        if math.isnan(google_df['rating'][row]):
            for col in result:
                result[col].pop(row)

    pd.DataFrame(result).to_csv("../Dataset/data.csv")
