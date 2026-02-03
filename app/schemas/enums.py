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


class FilterTopic(str, Enum):
    politics = "Politics"
    conflict_and_security = "Conflict & Security"
    crime = "Crime"
    business = "Business"
    economy = "Economy"
    technology = "Technology"
    health = "Health"
    environment = "Environment"
    society = "Society"
    sports = "Sports"
    entertainment = "Entertainment"


class Interval(str, Enum):
    hourly = "hourly"
    daily = "daily"