import argparse

from src.scraper.url_manager import URLManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def reset_url_queue():
    logger.info("Resetting URL queue...")
    url_manager = URLManager()
    url_manager.clear_all()
    logger.info("URL queue has been reset.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the URL queue.")
    parser.add_argument(
        "--confirm", action="store_true", help="Confirm resetting the URL queue"
    )
    args = parser.parse_args()

    if args.confirm:
        reset_url_queue()
    else:
        print("Please confirm resetting the URL queue by using the --confirm flag.")
