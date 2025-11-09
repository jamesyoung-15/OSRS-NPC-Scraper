import asyncio
from urllib.parse import urljoin
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from config.settings import settings
from src.storage.image_store import ImageStorageManager
from src.utils.helpers import url_to_filename, extract_npc_name_from_url
from src.utils.logger import setup_logger
from src.models.scraper_models import ImageDownloadResult, ImageUrlExtractionResult

logger = setup_logger(__name__)


class NPCImageExtractor:
    """Grabs the image link from an NPC page and downloads the image."""

    def __init__(self, image_store: Optional[ImageStorageManager] = None) -> None:
        self.image_store = image_store or ImageStorageManager()
        self.http_client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            follow_redirects=True,
        )

    def extract_image_url(self, html_content: str) -> ImageUrlExtractionResult:
        """Extract main NPC image url from the NPC page HTML content if available."""
        soup = BeautifulSoup(html_content, "html.parser")

        # if the npc has image, it's 99% of the time in the first image within this tag
        # eg. <a class="mw-file-description" href="/w/File:Example.png" ...
        img_link = soup.find("a", class_="mw-file-description")

        # it's possible for no image
        if not img_link:
            return ImageUrlExtractionResult(found=False, image_url=None)
        href = img_link.get("href")
        if not href:
            return ImageUrlExtractionResult(found=False, image_url=None)
        if not href.startswith(  # pyright: ignore[reportAttributeAccessIssue]
            "/w/File:"
        ):
            return ImageUrlExtractionResult(found=False, image_url=None)

        # the href looks like /w/File:Example.png
        # convert to /images/Example.png
        filename = href.replace(  # pyright: ignore[reportAttributeAccessIssue]
            "/w/File:", ""
        )
        image_url = urljoin(settings.wiki_base_url, f"/images/{filename}")

        logger.debug(f"Extracted NPC image URL: {image_url}")
        return ImageUrlExtractionResult(found=True, image_url=image_url)

    async def download_npc_image(self, image_url: str) -> ImageDownloadResult:
        """Fetch and store the NPC image from the given NPC page URL."""
        try:
            response = await self.http_client.get(image_url)
            response.raise_for_status()
            image_data = response.content

            npc_name = extract_npc_name_from_url(image_url)
            filename = url_to_filename(image_url, extension=None)
            print("askl;dfj;aklsdfj;asdfj")
            print(npc_name, filename)
            image_path = self.image_store.save(
                npc_name=npc_name, image_content=image_data, filename=filename
            )
            if not image_path:
                logger.error(f"Failed to save NPC image: {image_path}")
                return ImageDownloadResult(success=False, image_path=None)

            logger.info(f"Downloaded and saved NPC image: {image_path}")
            return ImageDownloadResult(success=True, image_path=str(image_path))
        except httpx.HTTPError as e:
            logger.error(f"Failed to download NPC image from {image_url}: {e}")
            return ImageDownloadResult(
                success=False, image_path=None, error_message=str(e)
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit async context manager."""
        await self.close()
