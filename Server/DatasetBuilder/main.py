from googleplaces import GooglePlaces, types, lang
import json
import decimal

# 32.836823, 35.056948 - T
# 32.758325, 35.022616 - B
# 32.789790, 35.075487 - R
# 32.805663, 34.956011 - L

# 32.797574, 35.015749 - C


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def get_google_api_key():
    try:
        with open('google-api-key.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        return None


def get_raw_data(google_api_key: str):
    lat_lng = {
        "lat": 32.797574,
        "lng": 35.015749
    }
    google_places = GooglePlaces(google_api_key)
    place_types = [types.TYPE_RESTAURANT, types.TYPE_CAFE]
    qr = google_places.nearby_search(language=lang.HEBREW, lat_lng=lat_lng, radius=5820, types=place_types)

    data = []
    for i in qr.places:
        i.get_details()
        data.append(i.details)

    return data


def write_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DecimalEncoder)


def main():
    key = get_google_api_key()
    if key is None:
        print("ERROR")
    else:
        write_to_file(get_raw_data(key), "raw-data.json")


if __name__ == '__main__':
    main()
