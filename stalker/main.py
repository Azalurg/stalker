import argparse
import sys
import logging

from stalker.src.scraper import Scraper
from stalker.src.parser import Parser


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logbook", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description="Stalker")
    parser.add_argument("--url", help="URL of the webpage to scrape", required=True)
    parser.add_argument("--name", help="Wallet name", required=True)
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== STALKER STARTED ===")

    try:
        url = args.url
        wallet_name = args.name

        # Step 1: Scrape webpage
        logger.info(f"Starting scraping webpage: {url}")
        scraper = Scraper()
        soup = scraper.fetch_page(url)
        if soup is None:
            logger.error("Failed to fetch the webpage")
            sys.exit(1)

        # Step 2: Parse the content
        parser = Parser(soup, wallet_name)
        snapshot = parser.make_snapshot()
        print(snapshot)

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
