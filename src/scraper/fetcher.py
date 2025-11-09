import asyncio
import random

import httpx

from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class FetchError(Exception):
    """Custom exception for fetch errors."""

    pass


class URLFetcher:
    """HTTP client for fetching Old School RuneScape Wiki pages."""

    def __init__(
        self,
        timout: int = settings.request_timeout,
        retries: int = settings.max_retries,
        rate_limit: int = settings.rate_limit_delay,
    ) -> None:
        self.client = httpx.AsyncClient(
            timeout=timout,
            follow_redirects=True,
        )
        self.timeout = timout
        self.retries = retries
        self.rate_limit = rate_limit

        logger.info(f"Initialized URLFetcher with timeout: {self.timeout}s")

    async def fetch_page(self, url: str) -> httpx.Response:
        """Fetch a Wiki page."""
        for attempt in range(1, self.retries + 1):
            try:
                await asyncio.sleep(
                    random.randint(self.rate_limit - 1, self.rate_limit + 3)
                )  # don't overwhelm wiki
                logger.debug(f"Fetching URL: {url} (Attempt {attempt}/{self.retries})")
                response = await self.client.get(url)
                response.raise_for_status()
                logger.info(
                    f"Successfully fetched URL: {url} (Status: {response.status_code})"
                )
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error for URL {url}: {e.response.status_code}")
                if attempt == self.retries:
                    raise FetchError(f"HTTP error: {e.response.status_code}") from e
            except httpx.TimeoutException as e:
                logger.warning(f"Timeout error for URL {url}: {e}")
                if attempt == self.retries:
                    raise FetchError("Request timed out") from e
            except httpx.RequestError as e:
                logger.warning(f"Request error for URL {url}: {e}")
                if attempt == self.retries:
                    raise FetchError(f"Request error: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error for URL {url}: {e}")
                raise FetchError(f"Unexpected error: {e}") from e

        logger.error(f"Failed to fetch URL after {self.retries} attempts: {url}")
        return response

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit async context manager."""
        await self.close()
