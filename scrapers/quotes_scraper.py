"""Quotes to Scrape scraper."""

import logging

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

START_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    """Scrapes every Quotes to Scrape page by following its Next link."""

    source_name = "Quotes to Scrape"

    def parse_page(self, html: str, page_url: str) -> tuple[list[dict], str | None]:
        soup = BeautifulSoup(html, "lxml")
        records = []

        for quote in soup.select("div.quote"):
            try:
                text_node = quote.select_one("span.text")
                author_node = quote.select_one("small.author")

                if not text_node or not author_node:
                    raise ValueError("missing quote text or author")

                tags = [
                    tag.get_text(" ", strip=True)
                    for tag in quote.select("a.tag")
                ]

                records.append({
                    "source": self.source_name,
                    "source_url": page_url,
                    "name_or_title": text_node.get_text(" ", strip=True),
                    "category": None,
                    "price_raw": None,
                    "rating_raw": None,
                    "author": author_node.get_text(" ", strip=True),
                    "tags": tags,
                    "description": None,
                })
            except Exception as exc:
                logger.warning("Skipping malformed quote record on %s: %s", page_url, exc)

        next_link = soup.select_one("li.next > a")
        next_url = self.next_url(page_url, next_link.get("href")) if next_link else None
        return records, next_url

    def scrape(self) -> list[dict]:
        url = START_URL
        page_number = 1
        all_records = []

        while url:
            logger.info("Quotes page %d: %s", page_number, url)
            html = self.fetch(url)
            if html is None:
                logger.error("Stopping Quotes to Scrape after failed page %d", page_number)
                break

            records, url = self.parse_page(html, url)
            all_records.extend(records)
            page_number += 1
            if url:
                self.pause()

        logger.info("Quotes to Scrape raw records: %d", len(all_records))
        return all_records
