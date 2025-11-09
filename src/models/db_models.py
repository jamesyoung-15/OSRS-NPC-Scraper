from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import mapped_column, Mapped

from src.storage.sql_db import SQLITE_BASE


class CrawledPage(SQLITE_BASE):
    """Model for crawled pages."""

    __tablename__ = "crawled_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    npc_name: Mapped[str] = mapped_column(String, nullable=False)
    has_image: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    image_url: Mapped[str] = mapped_column(String, nullable=True)
    image_filename: Mapped[str] = mapped_column(String, nullable=True)
    image_status: Mapped[str] = mapped_column(
        String, nullable=True, default="no_image"
    )  # success, not_found, failed, no_image
    image_size: Mapped[int] = mapped_column(
        Integer, nullable=True, default=0
    )  # in bytes

    status: Mapped[str] = mapped_column(
        String, nullable=False, default="failed"
    )  # success, failed, pending
    html_file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # in bytes

    crawled_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
