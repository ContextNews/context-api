from datetime import date, datetime, time, timedelta

from app.schemas.enums import FilterPeriod


def get_date_range(
    period: FilterPeriod,
    from_date: date | None,
    to_date: date | None,
) -> tuple[datetime, datetime]:
    if from_date and to_date:
        start = datetime.combine(from_date, time.min)
        end = datetime.combine(to_date + timedelta(days=1), time.min)
        return start, end

    today = date.today()
    if period == FilterPeriod.today:
        start_day = today
    elif period == FilterPeriod.week:
        start_day = today - timedelta(days=6)
    else:  # month
        start_day = today - timedelta(days=29)

    start = datetime.combine(start_day, time.min)
    end = datetime.combine(today + timedelta(days=1), time.min)
    return start, end
