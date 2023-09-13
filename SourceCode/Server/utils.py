import textdistance
import mpu


def text_distance(s1, s2):
    if not s1 and not s2:
        return 0
    return textdistance.strcmp95.normalized_similarity(s1, s2)


def location_distance(p1, p2):
    return mpu.haversine_distance(p1, p2)


def get_street_distance(cbs_street, g_street, g_reversed_street):
    return max(text_distance(cbs_street, g_street), text_distance(cbs_street, g_reversed_street))