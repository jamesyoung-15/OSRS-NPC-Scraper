from typing import Optional, List, Tuple
from urllib.parse import urljoin
import asyncio
from pathlib import Path

from bs4 import BeautifulSoup

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.helpers import extract_npc_name_from_url, url_to_filename
from src.scraper.url_manager import URLManager
from src.scraper.fetcher import URLFetcher, FetchError
from src.storage.html_store import HTMLStorageManager
from src.scraper.image_handler import NPCImageExtractor
from src.storage.sql_crud import SQLiteCRUDManager
from src.models.scraper_models import (
    CrawlAllNPCsResult,
    CrawlNPCListResult,
    CrawlNPCResult,
    CrawlStats,
    CrawlNPCListPageResult,
)

logger = setup_logger(__name__)


class WikiNPCSpider:
    """Spider to crawl NPC pages from the Old School RuneScape Wiki."""

    def __init__(
        self,
        fetcher: Optional[URLFetcher] = None,
        url_manager: Optional[URLManager] = None,
        html_store: Optional[HTMLStorageManager] = None,
        image_handler: Optional[NPCImageExtractor] = None,
        db_manager: Optional[SQLiteCRUDManager] = None,
        rate_limit: int = settings.rate_limit_delay,
    ) -> None:
        self.fetcher = fetcher or URLFetcher()
        self.url_manager = url_manager or URLManager()
        self.html_store = html_store or HTMLStorageManager()
        self.image_handler = image_handler or NPCImageExtractor()
        self.base_url = settings.wiki_base_url
        self.start_url = settings.wiki_npc_start_url
        self.db_manager = db_manager or SQLiteCRUDManager()
        self.rate_limit = rate_limit

        logger.info("Initialized WikiNPCSpider")

    def parse_npc_list_page(self, html_content: str) -> CrawlNPCListPageResult:
        """
        Parse NPC list page to extract NPC page URLs.

        Args:
            html_content: HTML content of the NPC list page.

        Returns:
            CrawlNPCListPageResult with NPC URLs and next page URL.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        npc_links = []
        next_page_url = None

        # Use the second div as npc list are below the first div
        content_divs = soup.find_all(name="div", attrs={"class": "mw-category"})
        if not content_divs:
            logger.warning("No category divs found on page")
            return CrawlNPCListPageResult(npc_urls=[], next_page_url=None)
        content_div = content_divs[1] if len(content_divs) > 1 else content_divs[0]

        # Extract NPC links
        for li in content_div.find_all(name="li"):
            link = li.find(name="a")
            if link and link.get("href"):
                full_url = urljoin(self.base_url, str(link["href"]))
                npc_links.append(full_url)

        logger.info(f"Found {len(npc_links)} NPC links on category page")

        # Find next page link
        next_page_link = soup.find(name="a", string="next page")  # type: ignore
        next_page_url = None

        if next_page_link and next_page_link.get("href"):
            next_page_url = urljoin(self.base_url, next_page_link["href"])
            logger.info(f"Found next page link: {next_page_url}")
        else:
            logger.info("No next page link found (last page)")

        return CrawlNPCListPageResult(npc_urls=npc_links, next_page_url=next_page_url)

    async def crawl_npc_page(self, npc_url: str) -> CrawlNPCResult:
        """Crawl and store a HTML and image of a single NPC wiki page."""
        npc_name = extract_npc_name_from_url(npc_url)
        filename = url_to_filename(npc_url)

        try:
            response = await self.fetcher.fetch_page(npc_url)
            html = response.text

            filepath = self.html_store.save(
                url=npc_url, filename=filename, html_content=html
            )
            html_file_size = filepath.stat().st_size

            has_image = False
            image_url = None
            image_filename = None
            image_file_path = None
            image_size_bytes = None
            image_status = "not_found"

            image_extract_result = self.image_handler.extract_image_url(html)
            image_url = image_extract_result.image_url

            if image_extract_result.found and image_url:
                image_status = "found"
                image_download_result = await self.image_handler.download_npc_image(
                    image_url
                )
                if image_download_result.success and image_download_result.image_path:
                    has_image = True
                    image_filename = url_to_filename(image_url, extension=None)
                    image_file_path = image_download_result.image_path
                    image_size_bytes = Path(image_file_path).stat().st_size
                    image_status = "success"
                    logger.info(f"Successfully downloaded image for NPC: {npc_name}")
                else:
                    self.url_manager.add_to_image_queue(
                        image_url=image_url, npc_name=npc_name, page_url=npc_url
                    )
            else:
                logger.info(f"No image found for NPC: {npc_name}")

            self.db_manager.add_crawled_page(
                url=npc_url,
                npc_name=npc_name,
                html_filename=str(filepath),
                status="success",
                html_file_size=html_file_size,
                image_url=image_url,
                image_filename=image_filename,
                image_status=image_status,
                image_size=image_size_bytes or 0,
                has_image=has_image,
            )

            self.url_manager.mark_visited(npc_url)
            logger.info(f"Successfully crawled NPC page: {npc_url}")
            return CrawlNPCResult(html_success=True, image_success=has_image)

        except FetchError as fe:
            logger.error(f"Fetch error for NPC page {npc_url}: {fe}")
            self.db_manager.add_crawled_page(
                url=npc_url,
                npc_name=npc_name,
                html_filename=filename,
                status="failed",
                html_file_size=0,
            )
            self.url_manager.mark_failed(npc_url, str(fe))
            return CrawlNPCResult(html_success=False, error_message=str(fe))

        except Exception as e:
            logger.error(f"Error crawling NPC page {npc_url}: {e}")
            self.url_manager.mark_failed(npc_url, str(e))
            return CrawlNPCResult(html_success=False, error_message=str(e))

    async def crawl_npc_list(
        self, start_url: str, max_pages: Optional[int] = None
    ) -> CrawlNPCListResult:
        """Crawl NPC category list pages to extract and queue NPC page URLs."""
        current_url: Optional[str] = start_url
        pages_crawled = 0
        total_queued = 0

        while current_url:
            pages_crawled += 1
            logger.info(f"Crawling NPC list page {pages_crawled}: {current_url}")

            try:
                response = await self.fetcher.fetch_page(current_url)
                html = response.text

                result = self.parse_npc_list_page(html)
                npc_links, next_page_url = result.npc_urls, result.next_page_url

                for npc_url in npc_links:
                    added = self.url_manager.add_to_queue(npc_url)
                    if added:
                        total_queued += 1

                logger.info(
                    f"Crawled NPC list page: {current_url} | "
                    f"NPCs queued: {len(npc_links)} | Total queued: {total_queued}"
                )

                if max_pages and pages_crawled >= max_pages:
                    logger.info(
                        f"Reached max pages limit: {max_pages}. Stopping crawl."
                    )
                    break

                current_url = next_page_url
            except FetchError as fe:
                logger.error(f"Fetch error for NPC list page {current_url}: {fe}")
                break
            except Exception as e:
                logger.error(f"Error crawling NPC list page {current_url}: {e}")
                break

        return CrawlNPCListResult(
            total_queued=total_queued, total_crawled=pages_crawled
        )

    async def crawl_all_npcs(
        self, max_npcs: Optional[int] = None
    ) -> CrawlAllNPCsResult:
        """
        Crawl all NPC pages from the URL queue. Make sure to populate the queue first.

        Args:
            max_npcs: Optional maximum number of NPC pages to crawl.

        Returns:
            CrawlAllNPCsResult with crawl statistics.

        """
        total_npcs_crawled = 0
        total_successful = 0
        total_failed = 0
        total_images_downloaded = 0
        total_image_failures = 0

        while True:
            if max_npcs and total_npcs_crawled >= max_npcs:
                logger.info(f"Reached max NPC crawl limit: {max_npcs}. Stopping crawl.")
                break

            npc_url = self.url_manager.get_next_url()
            if not npc_url:
                logger.info("No more NPC URLs in the queue. Crawling complete.")
                break

            result = await self.crawl_npc_page(npc_url)
            total_npcs_crawled += 1
            if result.html_success is True:
                total_successful += 1
            else:
                total_failed += 1
            if result.image_success:
                total_images_downloaded += 1
            else:
                total_image_failures += 1

        if total_npcs_crawled % 100 == 0:
            logger.info(
                f"Crawled all NPCs. Total crawled: {total_npcs_crawled}, "
                f"Total successful: {total_successful}, "
                f"Total failed: {total_failed}, "
                f"Total images downloaded: {total_images_downloaded}, "
                f"Total image failures: {total_image_failures}"
            )

        return CrawlAllNPCsResult(
            total_npcs_crawled=total_npcs_crawled,
            total_successful=total_successful,
            total_failed=total_failed,
            total_images_downloaded=total_images_downloaded,
            total_image_failures=total_image_failures,
        )

    async def run(
        self, max_pages: Optional[int] = None, max_npcs: Optional[int] = None
    ) -> CrawlStats:
        """Run the spider to crawl NPC list and all NPC pages."""

        logger.info("Starting NPC Scraper Spider")
        logger.info("1. Starting crawl of NPC list pages to populate queue")
        queue_result = await self.crawl_npc_list(
            self.start_url, max_pages=max_pages
        )

        logger.info("2. Starting crawl of all NPC pages from queue")
        crawl_result = await self.crawl_all_npcs(max_npcs=max_npcs)

        final_stats: CrawlStats = CrawlStats(
            total_npc_pages_crawled=crawl_result.total_npcs_crawled,
            total_npc_pages_successful=crawl_result.total_successful,
            total_npc_pages_failed=crawl_result.total_failed,
            total_image_downloads=crawl_result.total_images_downloaded,
            total_image_download_failures=crawl_result.total_image_failures,
            total_list_pages_crawled=queue_result.total_crawled,
        )

        return final_stats

    async def close(self) -> None:
        """Close any resources held by the spider."""
        if self.fetcher:
            await self.fetcher.close()
        if self.url_manager:
            self.url_manager.close()
        logger.info("Closed WikiNPCSpider resources")
