import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
        )
        logger.info(f"Scraper initialized (timeout: {self.timeout}s)")

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                logger.warning(f"Page might not be HTML: {content_type}")

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            logger.info(f"Page fetched successfully ({len(response.content)} bytes)")
            return soup

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error during page fetch: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during page fetch: {e}")
            return None
