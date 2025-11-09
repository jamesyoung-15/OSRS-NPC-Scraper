from typing import Optional, Tuple, List

from pydantic import BaseModel, Field


class CrawlStats(BaseModel):
    """Model to track crawling statistics."""

    total_list_pages_crawled: int = Field(
        default=0, description="Total NPC list pages crawled"
    )
    total_npc_pages_crawled: int = Field(
        default=0, description="Total NPC pages crawled"
    )
    total_npc_pages_successful: int = Field(
        default=0, description="Total successful NPC page crawls"
    )
    total_npc_pages_failed: int = Field(
        default=0, description="Total failed NPC page crawls"
    )
    total_image_downloads: int = Field(
        default=0, description="Total NPC images downloaded"
    )
    total_image_download_failures: int = Field(
        default=0, description="Total NPC image download failures"
    )


class CrawlNPCResult(BaseModel):
    """Model to represent the result of crawling an NPC page."""

    html_success: bool = Field(
        default=False, description="Indicates if the crawl was successful"
    )
    image_success: bool = Field(
        default=False, description="Indicates if the image download was successful"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if crawl failed"
    )


class CrawlNPCListResult(BaseModel):
    """Model to represent the result of crawling an NPC list page."""

    total_queued: int = Field(
        default=0, description="Total NPC URLs queued from the list page"
    )
    total_crawled: int = Field(default=0, description="Total NPC list pages crawled")


class CrawlNPCListPageResult(BaseModel):
    """Model to represent result of getting NPC URLs from a list page."""

    npc_urls: List[str] = Field(
        default_factory=list, description="List of NPC URLs extracted from the page"
    )
    next_page_url: Optional[str] = Field(
        default=None, description="URL of the next NPC list page if available"
    )


class CrawlAllNPCsResult(BaseModel):
    """Model to represent the result of crawling all NPC pages."""

    total_npcs_crawled: int = Field(
        default=0, description="Total number of NPCs crawled"
    )
    total_images_downloaded: int = Field(
        default=0, description="Total number of NPC images downloaded"
    )
    total_image_failures: int = Field(
        default=0, description="Total number of NPC image download failures"
    )
    total_successful: int = Field(
        default=0, description="Total number of successful NPC crawls"
    )
    total_failed: int = Field(
        default=0, description="Total number of failed NPC crawls"
    )


class QueueStats(BaseModel):
    """Model to track URL queue statistics."""

    total_urls_queued: int = Field(default=0, description="Total NPC URLs queued")
    total_urls_visited: int = Field(default=0, description="Total NPC URLs visited")
    total_urls_failed: int = Field(
        default=0, description="Total NPC URLs that failed to crawl"
    )


class ImageData(BaseModel):
    """Model to represent image data for retrying downloads."""

    image_url: str = Field(..., description="URL of the NPC image")
    npc_name: str = Field(..., description="Name of the NPC")
    page_url: str = Field(
        ..., description="URL of the NPC page where the image was found"
    )


class ImageUrlExtractionResult(BaseModel):
    """Model to represent the result of extracting an image URL from NPC page HTML."""

    image_url: Optional[str] = Field(
        default=None, description="Extracted image URL if available"
    )
    found: bool = Field(
        default=False, description="Indicates if an image URL was found"
    )


class ImageDownloadResult(BaseModel):
    """Model to represent the result of downloading an NPC image."""

    success: bool = Field(
        default=False, description="Indicates if the image download was successful"
    )
    image_path: Optional[str] = Field(
        default=None, description="Path where the image was saved"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if the download failed"
    )
