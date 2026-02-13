from app.services.news.news_sources_service import SOURCES, get_news_sources


class TestGetNewsSources:
    def test_returns_all_sources(self):
        result = get_news_sources()
        assert result is SOURCES
        assert len(result) > 0

    def test_all_sources_have_required_fields(self):
        for source in get_news_sources():
            assert source.source
            assert source.name
            assert source.url
            assert source.bias
            assert source.owner
            assert source.based
            assert isinstance(source.state_media, bool)

    def test_sources_contain_expected_outlets(self):
        names = {s.source for s in get_news_sources()}
        assert "BBC" in names
        assert "CNN" in names
        assert "The Guardian" in names

    def test_no_duplicate_urls(self):
        urls = [s.url for s in get_news_sources()]
        assert len(urls) == len(set(urls))
