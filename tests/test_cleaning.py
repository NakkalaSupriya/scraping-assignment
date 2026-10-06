from processing.cleaning import (
    clean_price,
    clean_rating,
    clean_tags,
    clean_text,
    normalize_url,
    strip_quotes,
)


def test_clean_text():
    assert clean_text("  Hello \n World \xa0") == "Hello World"


def test_strip_quotes():
    assert strip_quotes('“A quote”') == "A quote"


def test_clean_price():
    assert clean_price("£51.77") == 51.77


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3


def test_clean_tags():
    assert clean_tags(["Technology", "life", "Technology"]) == "life;technology"


def test_normalize_url():
    assert normalize_url("https://example.com/a") == "https://example.com/a"
    assert normalize_url("/relative") is None
