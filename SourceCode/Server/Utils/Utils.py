import textdistance
import mpu


def text_distance(s1, s2):
    if not s1 and not s2:
        return 0
    return textdistance.strcmp95.normalized_similarity(s1, s2)


def location_distance(p1, p2):
    return mpu.haversine_distance(p1, p2)


def is_closes_places(value1, value2, max_distance_km=0.3):
    return location_distance(value1, value2) < max_distance_km


def common_activity_hours(value1, value2, min_common_percentage=0.8):
    if value1 == (-1, -1) or value2 == (-1, -1):
        return False
    else:
        total_minutes = (value1[1] - value1[0]) + (value2[1] - value2[0])
        intersection_total_minutes = get_intersection_total_minutes(value1, value2)

        common = (intersection_total_minutes * 2) / total_minutes
        return common > min_common_percentage


def get_intersection_total_minutes(interval1, interval2):
    new_min = max(interval1[0], interval2[0])
    new_max = min(interval1[1], interval2[1])
    return new_max - new_min if new_min <= new_max else 0


def get_street_distance(cbs_street, g_street, g_reversed_street):
    return max(text_distance(cbs_street, g_street), text_distance(cbs_street, g_reversed_street))
