import time


class Time:

    ONE_DAY = 1440    # 24 * 60

    def __init__(self, time_as_str: str = None, total_minutes: int = None, hours: int = None, minutes: int = None):
        if time_as_str is not None:
            t = time.strptime(time_as_str, '%H%M')
            self.hours = t.tm_hour
            self.minutes = t.tm_min
        elif total_minutes is not None:
            self.hours = total_minutes / 60
            self.minutes = total_minutes % 60
        else:
            self.hours = hours
            self.minutes = minutes

    def get_total_minutes(self):
        return (self.hours * 60) + self.minutes

    def is_later_than(self, other: "Time"):
        return self.get_total_minutes() > other.get_total_minutes()

    def is_earlier_than(self, other: "Time"):
        return self.get_total_minutes() < other.get_total_minutes()

    def is_equals(self, other: "Time"):
        return self.get_total_minutes() == other.get_total_minutes()
