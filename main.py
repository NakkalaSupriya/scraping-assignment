"""Main ETL entry point for the web scraping assignment."""

import csv
import json
import logging
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

CSV_COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price",
    "rating", "author", "tags", "description", "scraped_at"
]


def configure_logging():
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def write_csv(records):
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows({key: record.get(key) for key in CSV_COLUMNS} for record in records)


def write_summary(summary):
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


def process_source(scraper, source_name):
    logger = logging.getLogger(__name__)
    raw_records = []
    try:
        raw_records = scraper.scrape()
    except Exception:
        logger.exception("Unexpected failure while scraping %s", source_name)
    finally:
        scraper.close()

    cleaned_records = []
    rejected = Counter()

    for raw in raw_records:
        raw["scraped_at"] = datetime.now(timezone.utc).isoformat()
        cleaned = clean_record(raw)
        problems = validate_record(cleaned)

        if problems:
            for reason in problems:
                rejected[reason] += 1
            logger.warning(
                "Rejected %s record: %s",
                source_name,
                ", ".join(problems),
            )
            continue

        cleaned_records.append(cleaned)

    return {
        "raw": raw_records,
        "cleaned": cleaned_records,
        "rejected": dict(rejected),
    }


def main():
    configure_logging()
    logger = logging.getLogger(__name__)
    start = time.perf_counter()
    start_time = datetime.now(timezone.utc)

    logger.info("Starting scraping ETL pipeline")

    books = process_source(BooksScraper(), "Books to Scrape")
    quotes = process_source(QuotesScraper(), "Quotes to Scrape")

    cleaned_all = books["cleaned"] + quotes["cleaned"]
    unique, duplicates = find_duplicates(cleaned_all)

    for duplicate in duplicates:
        logger.warning(
            "Duplicate removed: %s | %s",
            duplicate.get("source"),
            duplicate.get("name_or_title"),
        )

    write_csv(unique)

    end = time.perf_counter()
    end_time = datetime.now(timezone.utc)

    summary = {
        "sources": {
            "Books to Scrape": {
                "raw_records": len(books["raw"]),
                "cleaned_records": len(books["cleaned"]),
                "rejected_records": sum(books["rejected"].values()),
                "rejected_by_reason": books["rejected"],
            },
            "Quotes to Scrape": {
                "raw_records": len(quotes["raw"]),
                "cleaned_records": len(quotes["cleaned"]),
                "rejected_records": sum(quotes["rejected"].values()),
                "rejected_by_reason": quotes["rejected"],
            },
        },
        "duplicates_detected": len(duplicates),
        "final_record_count": len(unique),
        "start_time_utc": start_time.isoformat(),
        "end_time_utc": end_time.isoformat(),
        "duration_seconds": round(end - start, 3),
        "notes": [
            "Category and description are intentionally left empty because listing pages do not expose them reliably.",
            "Run `python main.py` with internet access to refresh the final dataset and summary."
        ],
    }
    write_summary(summary)

    logger.info("Final records: %d", len(unique))
    logger.info("Duplicates removed: %d", len(duplicates))
    logger.info("Pipeline complete")


if __name__ == "__main__":
    main()
