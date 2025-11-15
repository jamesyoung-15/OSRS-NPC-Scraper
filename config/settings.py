from typing import Optional
from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables or default values."""

    # Storage settings
    data_dir: str = Field(default="data", alias="DATA_DIR")
    raw_html_dir: str = Field(default=f"{data_dir}/raw_html/", alias="RAW_HTML_DIR")
    image_dir: str = Field(default=f"{data_dir}/images/", alias="IMAGE_DIR")
    sqlite_path: str = Field(
        default=f"{data_dir}/databases/osrs_npc.db", alias="DATABASE_PATH"
    )

    # Redis settings
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")

    # Scraper settings
    request_timeout: int = Field(default=10, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    rate_limit_delay: int = Field(default=3, alias="RATE_LIMIT_DELAY")
    wiki_base_url: str = Field(
        default="https://oldschool.runescape.wiki", alias="WIKI_BASE_URL"
    )
    wiki_npc_start_url: str = Field(
        default="https://oldschool.runescape.wiki/w/Category:Non-player_characters",
        alias="WIKI_NPC_START_URL",
    )

    # Logging
    log_dir: str = Field(default="data/logs/", alias="LOG_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def redis_url(self) -> str:
        """Construct the Redis URL from the host, port, and db."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
