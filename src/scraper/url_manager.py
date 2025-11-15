from typing import Optional
import json

import redis
from config.settings import settings
from src.utils.logger import setup_logger
from src.models.scraper_models import QueueStats, ImageData

logger = setup_logger(__name__)


class URLManager:
    """
    Manages URL queue and visited tracking using Redis.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize URL manager.

        Args:
            redis_client: Optional Redis client. If None, creates new client.
        """
        if redis_client is None:
            self.redis = redis.Redis(
                host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
            )
        else:
            self.redis = redis_client
        try:
            self.redis.ping()
            logger.info("Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        self.queue_key = "scraper:crawl_queue"
        self.visited_key = "scraper:visited_urls"
        self.failed_key = "scraper:failed_urls"
        self.image_queue_key = "scraper:image_retry_queue"

    def add_to_queue(self, url: str) -> bool:
        """
        Add URL to the queue if not already visited.

        Args:
            url: URL to add

        Returns:
            True if added, False if already visited
        """
        if self.is_visited(url):
            logger.debug(f"URL already visited, skipping: {url}")
            return False

        added = self.redis.sadd(self.queue_key, url)
        if added:
            logger.debug(f"Added to queue: {url}")
        return bool(added)

    def add_multiple_to_queue(self, urls: list[str]) -> int:
        """
        Add multiple URLs to the queue.

        Args:
            urls: List of URLs to add

        Returns:
            Number of URLs actually added
        """
        if not urls:
            return 0

        # Filter out already visited URLs
        new_urls = [url for url in urls if not self.is_visited(url)]

        if new_urls:
            added = self.redis.sadd(self.queue_key, *new_urls)
            logger.info(
                f"Added {added} URLs to queue (filtered {len(urls) - len(new_urls)} duplicates)"
            )
            return added  # type: ignore b/c not async

        logger.debug(f"All {len(urls)} URLs already visited")
        return 0

    def get_next_url(self) -> Optional[str]:
        """
        Get next URL from queue.

        Returns:
            URL string or None if queue is empty
        """
        url = self.redis.spop(self.queue_key)
        if url:
            logger.debug(f"Popped from queue: {url}")
            if isinstance(url, bytes):
                url = url.decode("utf-8")
        return url  # type: ignore b/c not async

    def mark_visited(self, url: str):
        """
        Mark URL as visited.

        Args:
            url: URL to mark as visited
        """
        self.redis.sadd(self.visited_key, url)
        logger.debug(f"Marked as visited: {url}")

    def is_visited(self, url: str) -> bool:
        """
        Check if URL has been visited.

        Args:
            url: URL to check

        Returns:
            True if visited, False otherwise
        """
        return bool(self.redis.sismember(self.visited_key, url))

    def mark_failed(self, url: str, error: str = ""):
        """
        Mark URL as failed.

        Args:
            url: URL that failed
            error: Optional error message
        """
        self.redis.hset(self.failed_key, url, error)
        logger.warning(f"Marked as failed: {url} - {error}")

    def add_to_image_queue(self, image_url: str, npc_name: str, page_url: str) -> bool:
        """Add failed image URL to the image retry queue."""
        image_data = ImageData(
            image_url=image_url,
            npc_name=npc_name,
            page_url=page_url,
        )
        added = self.redis.sadd(self.image_queue_key, image_data.model_dump_json())
        if added:
            logger.debug(f"Added to image retry queue: {image_data}")
        return bool(added)

    def get_next_image_data(self) -> Optional[ImageData]:
        """Get next image data from the image retry queue."""
        image_data_json = self.redis.spop(self.image_queue_key)
        if image_data_json:
            if isinstance(image_data_json, bytes):
                image_data_json = image_data_json.decode("utf-8")
            image_data = json.loads(image_data_json)  # type: ignore b/c not async
            try:
                image_data = ImageData.model_validate(image_data)
            except Exception as e:
                logger.error(f"Failed to validate image data: {e}")
                return None
            logger.debug(f"Popped from image retry queue: {image_data}")
            return image_data
        return None

    def get_image_queue_size(self) -> int:
        """Get current image retry queue size."""
        return self.redis.scard(self.image_queue_key)  # type: ignore b/c not async

    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self.redis.scard(self.queue_key)  # type: ignore b/c not async

    def get_visited_count(self) -> int:
        """Get count of visited URLs."""
        return self.redis.scard(self.visited_key)  # type: ignore b/c not async

    def get_failed_count(self) -> int:
        """Get count of failed URLs."""
        return self.redis.hlen(self.failed_key)  # type: ignore b/c not async

    def get_stats(self) -> QueueStats:
        """
        Get crawl statistics.

        Returns:
            QueueStats object with queue size, visited count, and failed count
        """
        return QueueStats(
            total_urls_queued=self.get_queue_size(),
            total_urls_visited=self.get_visited_count(),
            total_urls_failed=self.get_failed_count(),
        )

    def clear_all(self):
        """Clear all data (queue, visited, failed). Use with caution!"""
        self.redis.delete(
            self.queue_key, self.visited_key, self.failed_key, self.image_queue_key
        )
        logger.warning("Cleared all URL manager data")

    def close(self):
        """Close Redis connection."""
        self.redis.close()
        logger.info("Redis connection closed")
