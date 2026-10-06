"""Duplicate detection using normalized SHA-256 fingerprints."""

import hashlib
import re


def _normalize_key(value):
    text = str(value or "").lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def make_fingerprint(record):
    if record["source"] == "Books to Scrape":
        key = f'{record["source"]} {record["name_or_title"]}'
    else:
        key = (
            f'{record["source"]} {record.get("author", "")} '
            f'{record["name_or_title"][:50]}'
        )

    normalized = _normalize_key(key)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen = set()
    unique = []
    duplicates = []

    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)

    return unique, duplicates
