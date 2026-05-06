"""Text preprocessing utilities for SearchLens.

The implementation intentionally avoids external dependencies so that the
project can be run in a clean classroom environment.  The normalizer is kept
conservative: it lowercases, tokenizes alphanumeric terms, removes a small
stopword list, and applies a light suffix normalizer for common English forms.
"""

from __future__ import annotations

import re
from typing import Iterable, List

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z]+)?")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "in", "is", "it", "its", "of", "on", "or", "that", "the", "this",
    "to", "was", "were", "will", "with", "within", "into", "than", "then",
    "which", "while", "we", "our", "their", "they", "can", "may", "not",
    "no", "if", "using", "use", "used", "uses", "about", "between", "each",
    "such", "these", "those", "also", "when", "where", "how", "what", "why",
}


def normalize_token(token: str) -> str:
    """Return a normalized token.

    This is a light stemmer, not a full Porter implementation. It improves
    matching for common classroom retrieval examples without adding an external
    package dependency.
    """
    token = token.lower().strip("'")
    if token.endswith("'s") and len(token) > 3:
        token = token[:-2]
    if len(token) > 6 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 6 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 5 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """Tokenize and normalize text into index terms."""
    terms = [normalize_token(match.group(0)) for match in TOKEN_RE.finditer(text)]
    if remove_stopwords:
        terms = [term for term in terms if term and term not in STOPWORDS and len(term) > 1]
    return terms


def tokenize_keep_stopwords(text: str) -> List[str]:
    """Tokenize text while retaining stopwords, useful for phrase matching."""
    return [normalize_token(match.group(0)) for match in TOKEN_RE.finditer(text)]


def unique_terms(tokens: Iterable[str]) -> List[str]:
    """Return terms in first-seen order with duplicates removed."""
    seen = set()
    out: List[str] = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out
