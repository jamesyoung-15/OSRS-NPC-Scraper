from pathlib import Path
from typing import Optional

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.helpers import url_to_filename

logger = setup_logger(__name__)


class HTMLStorageManager:
    """Manages storage of HTML files for crawled NPC pages."""

    def __init__(self, storage_dir: str | Path = settings.raw_html_dir) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"HTML storage directory set to: {self.storage_dir}")

    def save(self, url: str, html_content: str, filename: Optional[str] = None) -> Path:
        """
        Save HTML content to file.

        Args:
            url: Source URL (used to generate filename if not provided)
            html_content: HTML content to save
            filename: Optional custom filename

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        if filename is None:
            filename = url_to_filename(url)

        filepath = self.storage_dir / filename

        try:
            filepath.write_text(html_content, encoding="utf-8")
            logger.info(f"Saved HTML to: {filepath} ({len(html_content)} bytes)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save HTML to {filepath}: {e}")
            raise IOError(f"Failed to save HTML: {e}") from e

    def load(self, filename: str) -> Optional[str]:
        """
        Load HTML content from file.

        Args:
            filename: Name of file to load

        Returns:
            HTML content or None if file doesn't exist
        """
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None

        try:
            content = filepath.read_text(encoding="utf-8")
            logger.debug(f"Loaded HTML from: {filepath} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Failed to load HTML from {filepath}: {e}")
            return None

    def exists(self, filename: str) -> bool:
        """
        Check if HTML file exists.

        Args:
            filename: Filename to check

        Returns:
            True if file exists, False otherwise
        """
        return (self.storage_dir / filename).exists()

    def get_filepath(self, filename: str) -> Path:
        """
        Get full path for a filename.

        Args:
            filename: Filename

        Returns:
            Full path
        """
        return self.storage_dir / filename

    def list_files(self) -> list[Path]:
        """
        List all HTML files in storage.

        Returns:
            List of file paths
        """
        return list(self.storage_dir.glob("*.html"))

    def get_file_count(self) -> int:
        """
        Get count of stored HTML files.

        Returns:
            Number of files
        """
        return len(self.list_files())
