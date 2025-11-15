import pytest

from src.scraper.fetcher import FetchError, URLFetcher


@pytest.mark.asyncio
async def test_fetch_success(httpx_mock):
    """Test successful fetch."""
    httpx_mock.add_response(
        url="https://example.com/test", text="<html>Test content</html>"
    )

    async with URLFetcher(rate_limit=0) as fetcher:
        content = await fetcher.fetch_page("https://example.com/test")
        assert content.text == "<html>Test content</html>"


@pytest.mark.asyncio
async def test_fetch_404_error(httpx_mock):
    """Test handling of 404 error."""
    httpx_mock.add_response(url="https://example.com/notfound", status_code=404)

    async with URLFetcher(rate_limit=0, retries=1) as fetcher:
        with pytest.raises(FetchError):
            await fetcher.fetch_page("https://example.com/notfound")
