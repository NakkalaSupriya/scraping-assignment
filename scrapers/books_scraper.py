"""Books to Scrape scraper."""

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

START_URL = "https://books.toscrape.com/"


class BooksScraper(BaseScraper):
    """Scrapes every Books to Scrape page by following its Next link."""

    source_name = "Books to Scrape"

    def parse_page(self, html: str, page_url: str) -> tuple[list[dict], str | None]:
        soup = BeautifulSoup(html, "lxml")
        records = []

        for article in soup.select("article.product_pod"):
            try:
                link = article.select_one("h3 > a")
                price = article.select_one("p.price_color")
                rating = article.select_one("p.star-rating")

                if not link:
                    raise ValueError("missing title/link element")

                rating_raw = " ".join(rating.get("class", [])) if rating else None
                records.append({
                    "source": self.source_name,
                    "source_url": urljoin(page_url, link.get("href", "")),
                    "name_or_title": link.get("title") or link.get_text(" ", strip=True),
                    "category": None,
                    "price_raw": price.get_text(" ", strip=True) if price else None,
                    "rating_raw": rating_raw,
                    "author": None,
                    "tags": None,
                    "description": None,
                })
            except Exception as exc:
                logger.warning("Skipping malformed book record on %s: %s", page_url, exc)

        next_link = soup.select_one("li.next > a")
        next_url = self.next_url(page_url, next_link.get("href")) if next_link else None
        return records, next_url

    def scrape(self) -> list[dict]:
        url = START_URL
        page_number = 1
        all_records = []

        while url:
            logger.info("Books page %d: %s", page_number, url)
            html = self.fetch(url)
            if html is None:
                logger.error("Stopping Books to Scrape after failed page %d", page_number)
                break

            records, url = self.parse_page(html, url)
            all_records.extend(records)
            page_number += 1
            if url:
                self.pause()

        logger.info("Books to Scrape raw records: %d", len(all_records))
        return all_records
