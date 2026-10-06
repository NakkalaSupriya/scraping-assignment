"""Shared HTTP session and pagination utilities."""

import logging
import time
from typing import Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Reusable HTTP helper for the two practice websites."""

    def __init__(self, delay: float = 0.5, timeout: int = 15):
        self.delay = delay
        self.timeout = timeout
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "ScrapingAssignment/1.0 (learning project)"
        })
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch(self, url: str) -> Optional[str]:
        """Fetch one URL and return UTF-8 decoded HTML, or None on failure."""
        try:
            logger.info("Request: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    def next_url(self, current_url: str, href: Optional[str]) -> Optional[str]:
        """Convert a relative next-page href to an absolute URL."""
        if not href:
            return None
        return urljoin(current_url, href)

    def pause(self) -> None:
        time.sleep(self.delay)

    def close(self) -> None:
        self.session.close()
