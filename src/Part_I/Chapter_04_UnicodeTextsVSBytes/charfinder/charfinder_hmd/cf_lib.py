"""
Unicode Character Finder Library

Provides core logic for searching Unicode characters by name using
strict substring matching and optional fuzzy matching.

Features:
- Unicode NFKD normalization for accurate matching
- Fuzzy matching using difflib with configurable threshold
- Unicode name index caching for performance
- Cleanly formatted output generation (U+XXXX, character, name, escape)

This is the backend for the CLI defined in cf_cli.py.

Example:
    from cf_lib import find_chars
    for line in find_chars("snowman"):
        print(line)

Author: HMDV
"""
import unicodedata
import difflib
import json
import os
import sys
from typing import Generator, Dict

CACHE_FILE = "unicode_name_cache.json"


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.
    """
    return unicodedata.normalize('NFKD', text).upper()


def build_name_cache() -> Dict[str, Dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names.
    Stores the result in a JSON file to avoid recomputation.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    cache = {}
    for code in range(sys.maxunicode + 1):
        char = chr(code)
        name = unicodedata.name(char, '')
        if name:
            cache[char] = {
                "original": name,
                "normalized": normalize(name)
            }

    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)

    return cache


NAME_CACHE = build_name_cache()


def find_chars(query: str, fuzzy: bool = False, threshold: float = 0.7) -> Generator[str, None, None]:
    """
    Generate a list of Unicode characters matching a query.
    Returns formatted string with codepoint, character, name, and escape code.
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")
    if not query.strip():
        return

    norm_query = normalize(query)
    matches = []

    for char, names in NAME_CACHE.items():
        if norm_query in names['normalized']:
            matches.append((ord(char), char, names['original']))

    if not matches and fuzzy:
        norm_names = {char: data['normalized'] for char, data in NAME_CACHE.items()}
        close = difflib.get_close_matches(norm_query, norm_names.values(), n=20, cutoff=threshold)
        for char, data in NAME_CACHE.items():
            if data['normalized'] in close:
                matches.append((ord(char), char, data['original']))

    for code, char, name in matches:
        code_str = f"U+{code:04X}".ljust(10)
        char_str = f"{char}".ljust(4)
        name_str = f"{name}".ljust(50) + f"(\\u{code:04x})"
        yield f"{code_str}  {char_str}  {name_str}"

