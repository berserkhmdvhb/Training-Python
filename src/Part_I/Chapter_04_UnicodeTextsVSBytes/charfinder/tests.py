"""
Unit tests for the Unicode Character Finder script (cf_optimized.py).
Tests both strict and fuzzy search behavior.

Run with:
    pytest tests.py

Requirements:
    pip install pytest
"""

import pytest
import unicodedata
import os
import json
from cf_optimized import find_chars, normalize, build_name_cache, CACHE_FILE


def test_strict_match():
    """Test that known strict matches return expected characters."""
    results = list(find_chars("snowman"))
    assert any("SNOWMAN" in line for line in results)
    assert any("U+2603" in line and "☃" in line for line in results)


def test_strict_match_case_insensitive():
    """Test that matching is case-insensitive."""
    results_lower = list(find_chars("snowman"))
    results_upper = list(find_chars("SNOWMAN"))
    assert results_lower == results_upper


def test_strict_match_accented():
    """Test that characters with diacritics can be found by logical name substring."""
    results = list(find_chars("acute"))
    assert any("LATIN SMALL LETTER E WITH ACUTE" in line for line in results)


def test_no_match_without_fuzzy():
    """Test that typos return nothing if fuzzy is disabled."""
    results = list(find_chars("smilng"))  # typo
    assert results == []


def test_fuzzy_match():
    """Test that fuzzy search finds close matches for misspelled input."""
    results = list(find_chars("grnning", fuzzy=True))  # typo of "grinning"
    assert any("GRINNING" in line for line in results)


def test_fuzzy_does_not_override_strict():
    """Fuzzy results should not replace strict matches when strict match exists."""
    strict = list(find_chars("heart"))
    fuzzy = list(find_chars("heart", fuzzy=True))
    assert strict == fuzzy


def test_output_format_fields():
    """Ensure output lines follow the format: U+XXXX<TAB>char<TAB>name  (\\uXXXX)"""
    results = list(find_chars("heart"))
    for line in results:
        parts = line.split("\t")
        assert len(parts) == 3
        assert parts[0].startswith("U+")
        assert parts[2].endswith(f"(\\u{ord(parts[1]):04x})")


def test_unicode_escape_format():
    """Ensure output lines contain valid Unicode escape sequences."""
    results = list(find_chars("heart"))
    for line in results:
        assert "\\u" in line
        assert line.startswith("U+")


def test_normalization_function():
    """Test normalize() returns uppercase normalized form."""
    assert normalize("é") == "E\u0301"
    assert normalize("café") == "CAFE\u0301"


def test_name_cache_exists():
    """Test the name cache is correctly created and reused."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    assert not os.path.exists(CACHE_FILE)
    cache = build_name_cache()
    assert os.path.exists(CACHE_FILE)
    assert isinstance(cache, dict)
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in cache.items())


def test_multiple_matches():
    """Test that a generic term returns multiple results."""
    results = list(find_chars("arrow"))
    assert len(results) > 10
    assert all("ARROW" in line for line in results)


def test_nfkd_decomposition_behavior():
    """Ensure that NFKD normalization helps match composed characters."""
    decomposed_query = normalize("é")
    assert decomposed_query == "E\u0301"

def test_fuzzy_threshold_effect():
    """Test that lowering threshold increases match count."""
    loose = list(find_chars("grnning", fuzzy=True, threshold=0.5))
    strict = list(find_chars("grnning", fuzzy=True, threshold=0.9))
    assert len(loose) >= len(strict)


def test_fuzzy_threshold_too_strict_returns_none():
    """Test that a very strict threshold may return no results."""
    results = list(find_chars("grnning", fuzzy=True, threshold=0.95))
    assert results == [] or all("GRINNING" in line for line in results)


def test_fuzzy_threshold_default_matches_explicit():
    """Test that the default threshold behaves same as 0.7 explicitly."""
    default = list(find_chars("grnning", fuzzy=True))
    explicit = list(find_chars("grnning", fuzzy=True, threshold=0.7))
    assert default == explicit
