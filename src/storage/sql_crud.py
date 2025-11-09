from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, mapped_column

from src.models.db_models import CrawledPage
from src.storage.sql_db import get_engine, get_session_factory, create_tables
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SQLiteCRUDManager:
    """SQLite CRUD database manager for handling connections and sessions."""

    def __init__(self, db_path: str = "") -> None:
        """Initialize the SQLiteCRUDManager with a database path."""
        self.engine = get_engine(db_path) if db_path else get_engine()
        create_tables(self.engine)
        self.SessionFactory = get_session_factory(self.engine)

    @contextmanager
    def get_session(self):
        """Context manager to get a database session."""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()

    def add_crawled_page(
        self,
        url: str,
        npc_name: str,
        html_filename: str,
        has_image: bool = False,
        image_url: Optional[str] = None,
        image_filename: Optional[str] = None,
        image_status: Optional[str] = None,
        image_size: int = 0,
        status: str = "success",
        html_file_size: int = 0,
    ) -> None:
        """Add a new crawled page record to the database."""
        with self.get_session() as session:
            crawled_page = session.query(CrawledPage).filter_by(url=url).first()
            if crawled_page:
                crawled_page.npc_name = npc_name
                crawled_page.content = html_filename
                crawled_page.status = status
                crawled_page.html_file_size = html_file_size
                crawled_page.has_image = has_image

                if image_url:
                    crawled_page.image_url = image_url
                if image_filename:
                    crawled_page.image_filename = image_filename
                if image_status:
                    crawled_page.image_status = image_status
                crawled_page.image_size = image_size

                crawled_page.updated_at = datetime.now(timezone.utc)
                logger.debug(f"Updated existing crawled page: {url}")
            else:
                new_page = CrawledPage(
                    url=url,
                    npc_name=npc_name,
                    content=html_filename,
                    status=status,
                    html_file_size=html_file_size,
                    crawled_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    has_image=has_image,
                )

                if image_url:
                    new_page.image_url = image_url
                if image_filename:
                    new_page.image_filename = image_filename
                if image_status:
                    new_page.image_status = image_status
                new_page.image_size = image_size

                session.add(new_page)
                logger.debug(f"Added new crawled page: {url}")

    def get_crawled_page(self, url: str) -> CrawledPage | None:
        """Retrieve a crawled page record by URL."""
        with self.get_session() as session:
            return session.query(CrawledPage).filter_by(url=url).first()

    def get_crawled_pages_by_status(self, status: str) -> list[CrawledPage]:
        """Retrieve all crawled pages with a specific status."""
        with self.get_session() as session:
            return session.query(CrawledPage).filter_by(status=status).all()

    def get_crawled_pages_by_npc_name(self, npc_name: str) -> list[CrawledPage]:
        """Retrieve all crawled pages with a specific NPC name."""
        with self.get_session() as session:
            pages = session.query(CrawledPage).filter_by(npc_name=npc_name).all()
            data = []
            for page in pages:
                data.append(
                    CrawledPage(
                        id=page.id,
                        url=page.url,
                        content=page.content,
                        npc_name=page.npc_name,
                        has_image=page.has_image,
                        image_url=page.image_url,
                        image_filename=page.image_filename,
                        image_status=page.image_status,
                        image_size=page.image_size,
                        status=page.status,
                        html_file_size=page.html_file_size,
                        crawled_at=page.crawled_at,
                        updated_at=page.updated_at,
                    )
                )
            return data

    def delete_crawled_page(self, url: str) -> None:
        """Delete a crawled page record by URL."""
        with self.get_session() as session:
            crawled_page = session.query(CrawledPage).filter_by(url=url).first()
            if crawled_page:
                session.delete(crawled_page)
                logger.debug(f"Deleted crawled page: {url}")
            else:
                logger.warning(f"Crawled page not found for deletion: {url}")

    def list_n_crawled_pages(self, n: int) -> list[CrawledPage]:
        """List the first N crawled pages."""
        with self.get_session() as session:
            pages = session.query(CrawledPage).limit(n).all()
            data = []
            for page in pages:
                data.append(
                    CrawledPage(
                        id=page.id,
                        url=page.url,
                        content=page.content,
                        npc_name=page.npc_name,
                        has_image=page.has_image,
                        image_url=page.image_url,
                        image_filename=page.image_filename,
                        image_status=page.image_status,
                        image_size=page.image_size,
                        status=page.status,
                        html_file_size=page.html_file_size,
                        crawled_at=page.crawled_at,
                        updated_at=page.updated_at,
                    )
                )
            return data
