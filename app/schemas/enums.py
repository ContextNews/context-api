from enum import StrEnum


class FilterPeriod(StrEnum):
    today = "today"
    last_24_hours = "last_24_hours"
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
    business = "business"
    conflict = "conflict"
    crime = "crime"
    economy = "economy"
    education = "education"
    entertainment = "entertainment"
    environment = "environment"
    geopolitics = "geopolitics"
    health = "health"
    law = "law"
    markets = "markets"
    politics = "politics"
    science = "science"
    society = "society"
    sports = "sports"
    technology = "technology"


class Interval(StrEnum):
    hourly = "hourly"
    daily = "daily"
