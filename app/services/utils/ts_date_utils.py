from datetime import date

from app.schemas.enums import TSFilterPeriod


def get_ts_date_range(
    period: TSFilterPeriod,
    from_date: date | None,
    to_date: date | None,
) -> tuple[date | None, date | None]:
    if from_date or to_date:
        return from_date, to_date

    if period == TSFilterPeriod.all_time:
        return None, None

    today = date.today()
    years = {
        TSFilterPeriod.one_year: 1,
        TSFilterPeriod.five_years: 5,
        TSFilterPeriod.ten_years: 10,
        TSFilterPeriod.twenty_years: 20,
    }[period]
    start = today.replace(year=today.year - years)
    return start, today
