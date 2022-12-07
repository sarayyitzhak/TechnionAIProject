from googleplaces import GooglePlaces, types, lang
import mpu
import json


# 32.836823, 35.056948 - T
# 32.758325, 35.022616 - B
# 32.789790, 35.075487 - R
# 32.805663, 34.956011 - L

# 32.797574, 35.015749 - C

def main():
    lat_lng = {
        "lat": 32.797574,
        "lng": 35.015749
    }
    google_places = GooglePlaces('AIzaSyDgs_N1LazwhtigvfhsSQ_Qt6BaZwhvh6U')
    qr = google_places.nearby_search(language=lang.HEBREW, lat_lng=lat_lng, radius=5820,
                                     types=[types.TYPE_RESTAURANT, types.TYPE_CAFE])

    data = []
    for i in qr.places:
        i.get_details()
        data.append(i.details)
        print(i)
        print('\n')

    print("ASD")

    # with open('data.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # print (qr.places)


def test():
    # Point one
    lat1 = 32.836823
    lon1 = 35.056948

    # Point two
    lat2 = 32.797574
    lon2 = 35.015749

    # What you were looking for
    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))
    print(dist * 1000)

    data = {
        "dist": "שרי"
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
