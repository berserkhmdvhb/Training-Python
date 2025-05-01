import pytest
import unicodedata
import os
import json
from cf_lib import find_chars, normalize, build_name_cache, CACHE_FILE


def test_strict_match():
    results = list(find_chars("snowman"))
    assert any("SNOWMAN" in line for line in results)
    assert any("U+2603" in line and "☃" in line for line in results)


def test_strict_match_case_insensitive():
    results_lower = list(find_chars("snowman"))
    results_upper = list(find_chars("SNOWMAN"))
    assert results_lower == results_upper


def test_strict_match_accented():
    results = list(find_chars("acute"))
    assert any("LATIN SMALL LETTER E WITH ACUTE" in line for line in results)


def test_no_match_without_fuzzy():
    results = list(find_chars("smilng"))
    assert results == []


def test_fuzzy_match():
    results = list(find_chars("grnning", fuzzy=True))
    assert any("GRINNING" in line for line in results)


def test_fuzzy_does_not_override_strict():
    strict = list(find_chars("heart"))
    fuzzy = list(find_chars("heart", fuzzy=True))
    assert strict == fuzzy


def test_output_format_fields():
    results = list(find_chars("heart"))
    for line in results:
        parts = line.split("\t")
        assert len(parts) == 3
        assert parts[0].startswith("U+")
        assert parts[2].endswith(f"(\\u{ord(parts[1]):04x})")


def test_unicode_escape_format():
    results = list(find_chars("heart"))
    for line in results:
        assert "\\u" in line
        assert line.startswith("U+")


def test_normalization_function():
    assert normalize("é") == "E\u0301"
    assert normalize("café") == "CAFE\u0301"


def test_name_cache_exists():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    assert not os.path.exists(CACHE_FILE)
    cache = build_name_cache()
    assert os.path.exists(CACHE_FILE)
    assert isinstance(cache, dict)
    assert all(isinstance(k, str) and isinstance(v, dict) for k, v in cache.items())


def test_multiple_matches():
    results = list(find_chars("arrow"))
    assert len(results) > 10
    assert all("ARROW" in line for line in results)


def test_nfkd_decomposition_behavior():
    decomposed_query = normalize("é")
    assert decomposed_query == "E\u0301"


def test_fuzzy_threshold_effect():
    loose = list(find_chars("grnning", fuzzy=True, threshold=0.5))
    strict = list(find_chars("grnning", fuzzy=True, threshold=0.9))
    assert len(loose) >= len(strict)


def test_fuzzy_threshold_too_strict_returns_none():
    results = list(find_chars("grnning", fuzzy=True, threshold=0.95))
    assert results == [] or all("GRINNING" in line for line in results)


def test_fuzzy_threshold_default_matches_explicit():
    default = list(find_chars("grnning", fuzzy=True))
    explicit = list(find_chars("grnning", fuzzy=True, threshold=0.7))
    assert default == explicit


def test_empty_query_returns_nothing():
    results = list(find_chars(""))
    assert results == []


def test_non_string_query_raises_typeerror():
    with pytest.raises(TypeError):
        list(find_chars(123))


def test_large_batch_query_execution():
    queries = ["arrow", "face", "hand", "circle", "star", "square"]
    for query in queries:
        results = list(find_chars(query))
        assert isinstance(results, list)
        assert len(results) > 0