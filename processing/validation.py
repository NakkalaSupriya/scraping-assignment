"""Record validation."""

import math

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record):
    problems = []

    if record.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")

    if not record.get("name_or_title"):
        problems.append("missing_name")

    url = str(record.get("source_url") or "")
    if not url.startswith(("http://", "https://")):
        problems.append("invalid_url")

    price = record.get("price")
    if price is not None:
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            problems.append("invalid_price")
        elif not math.isfinite(price) or price < 0:
            problems.append("invalid_price")

    rating = record.get("rating")
    if rating is not None and rating not in (1, 2, 3, 4, 5):
        problems.append("invalid_rating")

    return problems
