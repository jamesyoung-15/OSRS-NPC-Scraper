import pytest

from src.scraper.crawler import WikiNPCSpider


@pytest.fixture
def sample_npc_list_html() -> str:
    fixture_path = "tests/fixtures/Non-player_characters.html"

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_npc_list_page(sample_npc_list_html: str):

    crawler = WikiNPCSpider()

    result = crawler.parse_npc_list_page(sample_npc_list_html)
    npc_urls, next_page_url = result.npc_urls, result.next_page_url

    expected_npc_urls = {
        "https://oldschool.runescape.wiki/w/1337mage43",
        "https://oldschool.runescape.wiki/w/50%25_Luke",
    }
    for url in expected_npc_urls:
        assert url in npc_urls
    assert next_page_url is not None
    assert next_page_url.startswith(
        "https://oldschool.runescape.wiki/w/Category:Non-player_characters?pagefrom=A"
    )
