"""SearchLens: a compact, reproducible information retrieval project."""

from .index import Document, PositionalInvertedIndex
from .search import SearchEngine, SearchResult

__all__ = ["Document", "PositionalInvertedIndex", "SearchEngine", "SearchResult"]
__version__ = "1.0.0"
