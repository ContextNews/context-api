from enum import Enum

class FilterPeriod(str, Enum):
    today = "today"
    week = "week"
    month = "month"


class FilterRegion(str, Enum):
    north_america = "north_america"
    south_america = "south_america"
    europe = "europe"
    africa = "africa"
    middle_east = "middle_east"
    asia = "asia"
    oceania = "oceania"