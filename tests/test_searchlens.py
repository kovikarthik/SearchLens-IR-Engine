"""Regression tests for the SearchLens implementation."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from searchlens.index import PositionalInvertedIndex  # noqa: E402
from searchlens.search import SearchEngine  # noqa: E402


class SearchLensTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = PositionalInvertedIndex.from_jsonl(ROOT / "data" / "documents.jsonl")
        cls.engine = SearchEngine(cls.index)

    def test_index_statistics(self) -> None:
        stats = self.index.stats()
        self.assertEqual(stats["documents"], 60)
        self.assertGreater(stats["vocabulary"], 200)
        self.assertGreater(stats["postings"], 500)

    def test_bm25_retrieves_bm25_documents(self) -> None:
        results = self.engine.search("bm25 document length normalization", method="bm25", top_k=5)
        self.assertTrue(results)
        self.assertIn(results[0].category, {"bm25", "tfidf", "neural"})
        self.assertTrue(any(result.doc_id == "D012" for result in results[:3]))

    def test_phrase_query_uses_positions(self) -> None:
        results = self.engine.search('"information retrieval" phrase', method="bm25", top_k=5)
        self.assertTrue(any(result.doc_id == "D002" for result in results))

    def test_boolean_parser(self) -> None:
        hits = self.engine.boolean_search("bm25 AND baseline NOT pagerank")
        self.assertIn("D013", hits)
        self.assertNotIn("D027", hits)

    def test_pseudo_feedback_returns_ranked_results(self) -> None:
        results = self.engine.search("pseudo relevance feedback", method="bm25", top_k=5, pseudo_relevance=True)
        self.assertGreaterEqual(len(results), 3)
        self.assertEqual(results[0].category, "expansion")


if __name__ == "__main__":
    unittest.main()
