import asyncio
from typing import Optional
import argparse

from src.scraper.crawler import WikiNPCSpider
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def scrape_npcs(
    max_pages: Optional[int] = None, max_npcs: Optional[int] = None
) -> None:
    """Scrape NPC data from the Old School RuneScape Wiki."""
    spider = WikiNPCSpider()

    try:
        stats = await spider.run(max_pages=max_pages, max_npcs=max_npcs)
        print("Crawl completed.")
        print(f"Total NPC pages crawled: {stats.total_npc_pages_crawled}")
        print(f"Total NPC pages successful: {stats.total_npc_pages_successful}")
        print(f"Total NPC pages failed: {stats.total_npc_pages_failed}")
        print(f"Total image downloads: {stats.total_image_downloads}")
        print(f"Total image download failures: {stats.total_image_download_failures}")
        print(f"Total list pages crawled: {stats.total_list_pages_crawled}")
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred during scraping: {e}")
    finally:
        await spider.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape NPC data from the OSRS Wiki")
    parser.add_argument(
        "--max-pages", type=int, default=None, help="Maximum number of pages to scrape"
    )
    parser.add_argument(
        "--max-npcs", type=int, default=None, help="Maximum number of NPCs to scrape"
    )
    args = parser.parse_args()

    asyncio.run(scrape_npcs(max_pages=args.max_pages, max_npcs=args.max_npcs))
