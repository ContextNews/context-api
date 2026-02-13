from datetime import date, datetime, time
from unittest.mock import patch

from app.schemas.enums import FilterPeriod
from app.services.utils.date_utils import get_date_range


class TestGetDateRangeExplicitDates:
    def test_explicit_from_and_to(self):
        start, end = get_date_range(
            FilterPeriod.today,
            from_date=date(2025, 6, 1),
            to_date=date(2025, 6, 10),
        )
        assert start == datetime(2025, 6, 1, 0, 0, 0)
        assert end == datetime(2025, 6, 11, 0, 0, 0)

    def test_explicit_same_day(self):
        start, end = get_date_range(
            FilterPeriod.today,
            from_date=date(2025, 3, 15),
            to_date=date(2025, 3, 15),
        )
        assert start == datetime(2025, 3, 15, 0, 0, 0)
        assert end == datetime(2025, 3, 16, 0, 0, 0)

    def test_explicit_dates_override_period(self):
        """When both from/to dates and a period are provided, dates take priority."""
        start, end = get_date_range(
            FilterPeriod.month,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 1, 2),
        )
        assert start == datetime(2025, 1, 1, 0, 0, 0)
        assert end == datetime(2025, 1, 3, 0, 0, 0)


class TestGetDateRangePeriod:
    @patch("app.services.utils.date_utils.date")
    def test_today_period(self, mock_date):
        mock_date.today.return_value = date(2025, 7, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

        start, end = get_date_range(FilterPeriod.today, None, None)
        assert start == datetime(2025, 7, 15, 0, 0, 0)
        assert end == datetime(2025, 7, 16, 0, 0, 0)

    @patch("app.services.utils.date_utils.date")
    def test_week_period(self, mock_date):
        mock_date.today.return_value = date(2025, 7, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

        start, end = get_date_range(FilterPeriod.week, None, None)
        assert start == datetime(2025, 7, 9, 0, 0, 0)
        assert end == datetime(2025, 7, 16, 0, 0, 0)

    @patch("app.services.utils.date_utils.date")
    def test_month_period(self, mock_date):
        mock_date.today.return_value = date(2025, 7, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

        start, end = get_date_range(FilterPeriod.month, None, None)
        assert start == datetime(2025, 6, 16, 0, 0, 0)
        assert end == datetime(2025, 7, 16, 0, 0, 0)


class TestGetDateRangePartialDates:
    def test_only_from_date_falls_back_to_period(self):
        """If only from_date is set (to_date is None), period logic is used."""
        start, end = get_date_range(
            FilterPeriod.today,
            from_date=date(2025, 1, 1),
            to_date=None,
        )
        # from_date alone doesn't trigger the explicit path; period logic runs
        today = date.today()
        assert start == datetime.combine(today, time.min)

    def test_only_to_date_falls_back_to_period(self):
        """If only to_date is set (from_date is None), period logic is used."""
        start, end = get_date_range(
            FilterPeriod.today,
            from_date=None,
            to_date=date(2025, 12, 31),
        )
        today = date.today()
        assert start == datetime.combine(today, time.min)
