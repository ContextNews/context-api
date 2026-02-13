from enum import StrEnum


class FilterPeriod(StrEnum):
    today = "today"
    week = "week"
    month = "month"


class FilterRegion(StrEnum):
    north_america = "north_america"
    south_america = "south_america"
    europe = "europe"
    africa = "africa"
    middle_east = "middle_east"
    asia = "asia"
    oceania = "oceania"


class FilterTopic(StrEnum):
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


class Interval(StrEnum):
    hourly = "hourly"
    daily = "daily"
