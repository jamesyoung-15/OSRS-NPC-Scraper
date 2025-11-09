import pytest

from src.scraper.url_manager import URLManager


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis for testing without actual Redis connection."""

    class MockRedis:
        def __init__(self):
            self.data = {}
            self.sets = {}
            self.hashes = {}

        def ping(self):
            return True

        def sadd(self, key, *values):
            if key not in self.sets:
                self.sets[key] = set()
            initial_size = len(self.sets[key])
            self.sets[key].update(values)
            return len(self.sets[key]) - initial_size

        def spop(self, key):
            if key in self.sets and self.sets[key]:
                return self.sets[key].pop()
            return None

        def sismember(self, key, value):
            return value in self.sets.get(key, set())

        def scard(self, key):
            return len(self.sets.get(key, set()))

        def hset(self, key, field, value):
            if key not in self.hashes:
                self.hashes[key] = {}
            self.hashes[key][field] = value

        def hlen(self, key):
            return len(self.hashes.get(key, {}))

        def delete(self, *keys):
            for key in keys:
                self.sets.pop(key, None)
                self.hashes.pop(key, None)

        def close(self):
            pass

    return MockRedis()


@pytest.fixture
def url_manager(mock_redis):
    """Create a URLManager with mocked Redis."""
    return URLManager(redis_client=mock_redis)


def test_url_manager_initialization(mock_redis):
    """Test URLManager initialization."""
    manager = URLManager(redis_client=mock_redis)
    assert manager.redis is not None


def test_add_to_queue(url_manager):
    """Test adding URL to queue."""
    added = url_manager.add_to_queue("https://example.com/1")
    assert added is True

    # Adding same URL should return False
    added = url_manager.add_to_queue("https://example.com/1")
    assert added is False


def test_add_multiple_to_queue(url_manager):
    """Test adding multiple URLs."""
    urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]

    added = url_manager.add_multiple_to_queue(urls)
    assert added == 3
    assert url_manager.get_queue_size() == 3


def test_get_next_url(url_manager):
    """Test getting next URL from queue."""
    url_manager.add_to_queue("https://example.com/1")
    url_manager.add_to_queue("https://example.com/2")

    url = url_manager.get_next_url()
    assert url in ["https://example.com/1", "https://example.com/2"]
    assert url_manager.get_queue_size() == 1


def test_mark_visited(url_manager):
    """Test marking URL as visited."""
    url = "https://example.com/visited"

    assert url_manager.is_visited(url) is False
    url_manager.mark_visited(url)
    assert url_manager.is_visited(url) is True


def test_mark_failed(url_manager):
    """Test marking URL as failed."""
    url_manager.mark_failed("https://example.com/failed", "404 error")
    assert url_manager.get_failed_count() == 1


def test_get_stats(url_manager):
    """Test getting statistics."""
    url_manager.add_to_queue("https://example.com/1")
    url_manager.mark_visited("https://example.com/visited")
    url_manager.mark_failed("https://example.com/failed", "error")

    stats = url_manager.get_stats()
    assert stats.total_urls_queued == 1
    assert stats.total_urls_visited == 1
    assert stats.total_urls_failed == 1


def test_clear_all(url_manager):
    """Test clearing all data."""
    url_manager.add_to_queue("https://example.com/1")
    url_manager.mark_visited("https://example.com/2")

    url_manager.clear_all()

    stats = url_manager.get_stats()
    assert stats.total_urls_queued == 0
    assert stats.total_urls_visited == 0
