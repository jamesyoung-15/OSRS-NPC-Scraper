from pathlib import Path
from typing import Optional

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.helpers import url_to_filename

logger = setup_logger(__name__)


class ImageStorageManager:
    """Handles storage of image files for NPC images."""

    def __init__(self, storage_dir: str | Path = settings.image_dir) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image storage directory set to: {self.storage_dir}")

    def save(
        self, npc_name: str, image_content: bytes, filename: Optional[str] = None
    ) -> Path:
        """
        Save image content to file.

        Args:
            npc_name: Name of the NPC (used to generate filename if not provided)
            image_content: Image content to save
            filename: Optional custom filename

        Returns:
            Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        if filename is None:
            filename = url_to_filename(npc_name, extension=None)

        filepath = self.storage_dir / filename

        try:
            filepath.write_bytes(image_content)
            logger.info(f"Saved image to: {filepath} ({len(image_content)} bytes)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save image to {filepath}: {e}")
            raise IOError(f"Failed to save image: {e}") from e

    def load(self, filename: str) -> Optional[bytes]:
        """
        Load image content from file.

        Args:
            filename: Name of file to load

        Returns:
            Image content or None if file doesn't exist
        """
        filepath = self.storage_dir / filename

        if not filepath.exists():
            logger.warning(f"Image file does not exist: {filepath}")
            return None

        try:
            content = filepath.read_bytes()
            logger.info(f"Loaded image from: {filepath} ({len(content)} bytes)")
            return content
        except Exception as e:
            logger.error(f"Failed to load image from {filepath}: {e}")
            return None

    def exists(self, filename: str) -> bool:
        """
        Check if image file exists.

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
        return list(self.storage_dir.glob("*.png"))

    def get_file_count(self) -> int:
        """
        Get count of stored image files.

        Returns:
            Number of files
        """
        return len(self.list_files())
