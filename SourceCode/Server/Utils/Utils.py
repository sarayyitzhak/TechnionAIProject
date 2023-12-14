import textdistance
import mpu
from SourceCode.Server.Utils.Time import Time


def text_distance(s1, s2):
    if not s1 and not s2:
        return 0
    return textdistance.strcmp95.normalized_similarity(s1, s2)


def location_distance(p1, p2):
    return mpu.haversine_distance(p1, p2)


def is_closes_places(value1, value2, max_distance_km=0.3):
    return location_distance(value1, value2) < max_distance_km


def is_time_bigger(value1, value2):
    if value1 == value2:
        return True
    elif value1 == -1 or value2 == -1:
        return False
    else:
        return value2 >= value1


def get_street_distance(cbs_street, g_street, g_reversed_street):
    return max(text_distance(cbs_street, g_street), text_distance(cbs_street, g_reversed_street))


def is_open_on_saturday(friday_activity, saturday_activity):
    if friday_activity is None or saturday_activity is None:
        return None
    latest_closing_time_friday = Time(hours=17, minutes=0)
    earliest_opening_time_saturday = Time(hours=19, minutes=0)
    open_on_friday = Time(total_minutes=friday_activity[1]).is_later_than(latest_closing_time_friday)
    open_on_saturday = Time(total_minutes=saturday_activity[0]).is_earlier_than(earliest_opening_time_saturday) and saturday_activity[0] != -1
    return open_on_friday or open_on_saturday


class AppException(Exception):

    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self) -> str:
        return self.msg
