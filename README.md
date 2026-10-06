# Web Scraping & Data Processing Assignment

## 1. Overview

This project implements a Python ETL pipeline for two public scraping practice websites:

- Books to Scrape — https://books.toscrape.com/
- Quotes to Scrape — https://quotes.toscrape.com/

The workflow is:

**Scrape → Clean → Validate → Deduplicate → Consolidate → Save**

The implementation follows the assignment requirements: separate source scrapers, dynamic pagination, reusable cleaning functions, validation, duplicate detection, logging, tests, and reproducible setup.

## 2. Requirements

- Python 3.10–3.12
- Internet access
- Windows, macOS, or Linux

## 3. Project Structure

```text
scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── tests/
│   ├── test_cleaning.py
│   ├── test_validation.py
│   └── test_deduplication.py
├── output/
│   ├── final_dataset.csv
│   └── summary_report.json
├── logs/
│   └── scraper.log
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 4. Installation

### Windows Command Prompt

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Run

From the project root:

```bash
python main.py
```

The program creates/refreshes:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

The scraper follows each site's `li.next > a` link until there is no next page. It does not hard-code a page count.

## 6. Source Parsing

### Books to Scrape

- Record: `article.product_pod`
- Title/link: `h3 > a`
- Price: `p.price_color`
- Rating: class on `p.star-rating`
- Pagination: `li.next > a`

### Quotes to Scrape

- Record: `div.quote`
- Quote: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Pagination: `li.next > a`

The source observations and common schema follow the supplied assignment specification. 

## 7. Common Data Model

| Column | Books | Quotes |
|---|---|---|
| `source` | Books to Scrape | Quotes to Scrape |
| `source_url` | Book detail URL | Page URL containing quote |
| `name_or_title` | Book title | Quote text |
| `category` | Empty unless sourced from detail page | Empty |
| `price` | Numeric price | Empty |
| `rating` | 1–5 integer | Empty |
| `author` | Empty | Author |
| `tags` | Empty | Lowercase sorted tags joined by `;` |
| `description` | Empty | Empty |
| `scraped_at` | UTC timestamp | UTC timestamp |

Category and description are intentionally not guessed. The assignment allows source-specific fields to remain empty when they do not apply or are not safely available.

## 8. Cleaning

Cleaning is separated from scraping:

- whitespace and non-breaking-space cleanup
- curly quote removal
- `£51.77` → `51.77`
- `Three` → `3`
- lowercase, sort, and deduplicate tags
- URL normalization

## 9. Validation

Each cleaned record is checked for:

- known source
- non-empty identifying name/text
- HTTP/HTTPS source URL
- non-negative numeric price when present
- rating in the range 1–5 when present

Invalid records are rejected without stopping the whole pipeline, and rejection reasons are counted.

## 10. Duplicate Detection

Duplicates are removed.

- Books: source + title
- Quotes: source + author + first 50 characters of quote text

Before hashing, the key is lowercased, punctuation is removed, and whitespace is collapsed. This means differences such as:

```text
Example Book Title
 Example Book Title
EXAMPLE BOOK TITLE
```

are treated as the same record.

A unit test deliberately creates duplicates to prove the logic works.

## 11. Error Handling and Reliability

The shared HTTP helper uses:

- `requests.Session`
- a descriptive User-Agent
- timeout handling
- retries for temporary HTTP statuses such as 429, 500, 502, 503 and 504
- a 0.5 second delay between page requests

A failed source is logged and does not prevent the other source from being processed.

## 12. Logging

`logs/scraper.log` records:

- requests/pages
- warnings for malformed/rejected records
- errors for failed requests
- duplicate removals
- final record and duplicate counts

## 13. Tests

Run:

```bash
pytest -q
```

Tests cover:

- text, quote, price, rating, tag and URL cleaning
- validation failures
- duplicate detection with case/space differences

The unit tests do not require internet access.

## 14. Outputs

`output/final_dataset.csv` is the consolidated standardized dataset.

`output/summary_report.json` contains:

- raw records per source
- cleaned records per source
- rejected records and reasons
- duplicate count
- final record count
- UTC start/end times
- duration

The assignment requires these consolidated outputs and summary metrics. 

## 15. Important Note About the Included Output

This ZIP contains a small **sample execution output** so the required output files are present even when the package is opened offline.

For the actual submission run, activate the virtual environment, install dependencies, and execute:

```bash
python main.py
```

That command replaces the sample CSV, JSON report, and log with the live results from both practice websites.

The current build environment used to prepare this ZIP has no external DNS/network access, so a live 1,100-record scrape could not be executed here. The scraper itself is designed for the required live run.

## 16. Assumptions and Limitations

1. Only the two supplied public practice websites are scraped.
2. No authentication, CAPTCHA, robots restriction, or access-control bypass is attempted.
3. Category and description are left empty rather than guessed.
4. The quote `source_url` is the page where the quote appeared.
5. Duplicate records are removed rather than flagged.
6. The default run follows all available pagination links until no `Next` link exists.
7. A temporary network failure can cause that source to stop after retries; the other source still runs.

## 17. AI Usage

See `AI_USAGE.md`. The assignment explicitly permits AI assistance but requires the candidate to understand, review, test, and correct AI-generated code. 

## 18. Interview Questions to Prepare

- Why Requests + BeautifulSoup?
- How does pagination work?
- How are missing fields handled?
- How are failed requests handled?
- How does duplicate detection work?
- Why this standardized schema?
- Which parts were AI-assisted?
- How did you test the final implementation?
- What would you change for production?

## 19. Reproducibility Checklist

```text
[ ] Python 3.10–3.12 installed
[ ] Virtual environment created
[ ] requirements.txt installed
[ ] python main.py completed
[ ] Both sources appear in final_dataset.csv
[ ] summary_report.json final count matches CSV rows
[ ] logs/scraper.log contains page/request information
[ ] pytest -q passes
```
