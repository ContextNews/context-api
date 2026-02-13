from app.queries.news.stories_queries import REGION_COUNTRY_CODES
from app.schemas.enums import FilterRegion


class TestRegionCountryCodes:
    def test_all_regions_present(self):
        for region in FilterRegion:
            assert region in REGION_COUNTRY_CODES

    def test_no_empty_regions(self):
        for region, codes in REGION_COUNTRY_CODES.items():
            assert len(codes) > 0, f"{region} has no country codes"

    def test_codes_are_three_letter_strings(self):
        for region, codes in REGION_COUNTRY_CODES.items():
            for code in codes:
                assert len(code) == 3, f"Code {code} in {region} is not 3 letters"
                assert code.isalpha(), f"Code {code} in {region} is not alphabetic"
                assert code.isupper(), f"Code {code} in {region} is not uppercase"

    def test_no_duplicate_codes_across_regions(self):
        seen: dict[str, FilterRegion] = {}
        for region, codes in REGION_COUNTRY_CODES.items():
            for code in codes:
                assert code not in seen, (
                    f"Code {code} appears in both {seen[code].value} and {region.value}"
                )
                seen[code] = region

    def test_major_countries_in_expected_regions(self):
        assert "USA" in REGION_COUNTRY_CODES[FilterRegion.north_america]
        assert "GBR" in REGION_COUNTRY_CODES[FilterRegion.europe]
        assert "CHN" in REGION_COUNTRY_CODES[FilterRegion.asia]
        assert "BRA" in REGION_COUNTRY_CODES[FilterRegion.south_america]
        assert "NGA" in REGION_COUNTRY_CODES[FilterRegion.africa]
        assert "SAU" in REGION_COUNTRY_CODES[FilterRegion.middle_east]
        assert "AUS" in REGION_COUNTRY_CODES[FilterRegion.oceania]
