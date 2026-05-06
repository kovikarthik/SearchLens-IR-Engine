"""Retrieval models and query processing for SearchLens."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import html
import math
import re
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .index import PositionalInvertedIndex
from .preprocess import normalize_token, tokenize, tokenize_keep_stopwords, unique_terms
from .utils.logger import get_logger

logger = get_logger("searchlens.search")


@dataclass
class SearchResult:
    doc_id: str
    title: str
    score: float
    snippet: str
    category: str
    url: str = ""
    explanation: str = ""


class SearchEngine:
    """Search interface over a PositionalInvertedIndex."""

    def __init__(self, index: PositionalInvertedIndex) -> None:
        self.index = index
        self._doc_norm_cache: Dict[str, float] = {}

    def idf(self, term: str) -> float:
        """BM25 inverse document frequency with Robertson/Sparck Jones smoothing."""
        n_docs = max(len(self.index), 1)
        df = self.index.document_frequency(term)
        return math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))

    def bm25_score(self, doc_id: str, query_terms: Sequence[str], k1: float = 1.5, b: float = 0.75) -> float:
        score = 0.0
        doc_len = max(self.index.doc_lengths.get(doc_id, 0), 1)
        avg_len = max(self.index.avg_doc_length, 1.0)
        qtf = Counter(query_terms)
        for term, q_count in qtf.items():
            tf = self.index.term_frequency(doc_id, term)
            if tf <= 0:
                continue
            denom = tf + k1 * (1.0 - b + b * doc_len / avg_len)
            score += self.idf(term) * ((tf * (k1 + 1.0)) / denom) * (1.0 + math.log(q_count))
        return score

    def tfidf_doc_norm(self, doc_id: str) -> float:
        if doc_id in self._doc_norm_cache:
            return self._doc_norm_cache[doc_id]
        counter = Counter(self.index.doc_tokens.get(doc_id, []))
        total = 0.0
        for term, tf in counter.items():
            weight = (1.0 + math.log(tf)) * self.idf(term)
            total += weight * weight
        norm = math.sqrt(total) or 1.0
        self._doc_norm_cache[doc_id] = norm
        return norm

    def tfidf_score(self, doc_id: str, query_terms: Sequence[str]) -> float:
        q_counter = Counter(query_terms)
        q_norm_sq = 0.0
        dot = 0.0
        for term, qtf in q_counter.items():
            q_weight = (1.0 + math.log(qtf)) * self.idf(term)
            q_norm_sq += q_weight * q_weight
            dtf = self.index.term_frequency(doc_id, term)
            if dtf > 0:
                d_weight = (1.0 + math.log(dtf)) * self.idf(term)
                dot += q_weight * d_weight
        q_norm = math.sqrt(q_norm_sq) or 1.0
        return dot / (q_norm * self.tfidf_doc_norm(doc_id))

    def overlap_score(self, doc_id: str, query_terms: Sequence[str]) -> float:
        """Simple Boolean-style baseline: more matched unique terms ranks higher."""
        terms = set(query_terms)
        if not terms:
            return 0.0
        matched = sum(1 for term in terms if self.index.term_frequency(doc_id, term) > 0)
        coverage = matched / len(terms)
        tf_sum = sum(min(3, self.index.term_frequency(doc_id, term)) for term in terms)
        return coverage + 0.05 * tf_sum

    @staticmethod
    def _extract_phrases(query: str) -> Tuple[List[List[str]], str]:
        phrases: List[List[str]] = []

        def repl(match: re.Match[str]) -> str:
            phrase = match.group(1)
            tokens = tokenize_keep_stopwords(phrase)
            if tokens:
                phrases.append(tokens)
            return " "

        remainder = re.sub(r'"([^"]+)"', repl, query)
        return phrases, remainder

    def expand_query(self, query_terms: Sequence[str], feedback_doc_ids: Sequence[str], expansion_terms: int = 3) -> List[str]:
        """Pseudo relevance feedback expansion using top tf-idf terms.

        The expansion is intentionally conservative: it appends at most three
        high-idf terms from the first pass and never duplicates an original term.
        """
        original = set(query_terms)
        scores: Dict[str, float] = defaultdict(float)
        for rank, doc_id in enumerate(feedback_doc_ids, start=1):
            rank_discount = 1.0 / rank
            counter = Counter(self.index.doc_tokens.get(doc_id, []))
            for term, tf in counter.items():
                if term in original or len(term) <= 2:
                    continue
                scores[term] += rank_discount * (1.0 + math.log(tf)) * self.idf(term)
        selected = [term for term, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:expansion_terms]]
        return list(query_terms) + selected

    def search(
        self,
        query: str,
        method: str = "bm25",
        top_k: int = 10,
        pseudo_relevance: bool = False,
        feedback_docs: int = 3,
        expansion_terms: int = 3,
    ) -> List[SearchResult]:
        start_time = time.time()
        logger.info(f"Query: '{query}' | Method: {method} | PRF: {pseudo_relevance}")
        method = method.lower().strip()
        phrases, remainder = self._extract_phrases(query)
        query_terms = tokenize(remainder, remove_stopwords=True)
        for phrase in phrases:
            query_terms.extend([term for term in phrase if term not in {"the", "a", "an", "of", "to"}])
        query_terms = [term for term in query_terms if term]
        query_terms_unique = unique_terms(query_terms)
        if not query_terms_unique and not phrases:
            return []

        candidate_docs = self.index.documents_for_terms(query_terms_unique)
        if not candidate_docs and phrases:
            candidate_docs = set(self.index.documents.keys())
        for phrase_terms in phrases:
            candidate_docs = {doc_id for doc_id in candidate_docs if self.index.contains_phrase(doc_id, phrase_terms)}

        if pseudo_relevance and method == "bm25" and query_terms_unique:
            first_pass = self._rank_candidates(candidate_docs, query_terms_unique, method, top_k=max(feedback_docs, top_k))
            feedback_ids = [doc_id for doc_id, _ in first_pass[:feedback_docs]]
            query_terms_unique = self.expand_query(query_terms_unique, feedback_ids, expansion_terms=expansion_terms)
            candidate_docs = self.index.documents_for_terms(query_terms_unique)
            for phrase_terms in phrases:
                candidate_docs = {doc_id for doc_id in candidate_docs if self.index.contains_phrase(doc_id, phrase_terms)}

        ranked = self._rank_candidates(candidate_docs, query_terms_unique, method, top_k=top_k)
        results = [self._make_result(doc_id, score, query_terms_unique, phrases) for doc_id, score in ranked[:top_k]]
        latency = (time.time() - start_time) * 1000
        logger.info(f"Results: {len(results)} | Latency: {latency:.2f}ms")
        return results

    def _rank_candidates(self, candidate_docs: Iterable[str], query_terms: Sequence[str], method: str, top_k: int) -> List[Tuple[str, float]]:
        scored: List[Tuple[str, float]] = []
        for doc_id in candidate_docs:
            if method == "bm25":
                score = self.bm25_score(doc_id, query_terms)
            elif method == "tfidf":
                score = self.tfidf_score(doc_id, query_terms)
            elif method in {"boolean", "overlap"}:
                score = self.overlap_score(doc_id, query_terms)
            else:
                raise ValueError(f"Unknown search method: {method}")
            if score > 0:
                scored.append((doc_id, score))
        return sorted(scored, key=lambda item: (-item[1], item[0]))[:top_k]

    def _make_result(self, doc_id: str, score: float, query_terms: Sequence[str], phrases: Sequence[Sequence[str]]) -> SearchResult:
        doc = self.index.documents[doc_id]
        top_terms = ", ".join(f"{term}:{tf}" for term, tf in self.index.top_terms(doc_id, limit=4))
        return SearchResult(
            doc_id=doc.doc_id,
            title=doc.title,
            score=score,
            snippet=self.snippet(doc.body, query_terms),
            category=doc.category,
            url=doc.url,
            explanation=f"matched terms; top document terms: {top_terms}",
        )

    def snippet(self, text: str, query_terms: Sequence[str], window: int = 190) -> str:
        if not text:
            return ""
        lower = text.lower()
        start = 0
        for term in query_terms:
            pos = lower.find(term.lower())
            if pos != -1:
                start = max(pos - window // 4, 0)
                break
        end = min(start + window, len(text))
        raw = text[start:end]
        if start > 0:
            raw = "..." + raw
        if end < len(text):
            raw += "..."
        escaped = html.escape(raw)
        for term in sorted(set(query_terms), key=len, reverse=True):
            if len(term) > 2:
                escaped = re.sub(f"(?i)({re.escape(term)})", r"<mark>\1</mark>", escaped)
        return escaped

    def boolean_search(self, expression: str) -> List[str]:
        """Evaluate a simple Boolean expression with AND, OR, NOT, and parentheses."""
        universe = set(self.index.documents.keys())
        tokens = re.findall(r"\(|\)|AND|OR|NOT|[A-Za-z0-9_\-]+", expression, flags=re.IGNORECASE)
        output: List[str] = []
        operators: List[str] = []
        precedence = {"NOT": 3, "AND": 2, "OR": 1}

        def push_operator(op: str) -> None:
            while operators and operators[-1] != "(" and precedence.get(operators[-1], 0) >= precedence.get(op, 0):
                output.append(operators.pop())
            operators.append(op)

        for token in tokens:
            upper = token.upper()
            if upper in precedence:
                push_operator(upper)
            elif token == "(":
                operators.append(token)
            elif token == ")":
                while operators and operators[-1] != "(":
                    output.append(operators.pop())
                if operators and operators[-1] == "(":
                    operators.pop()
            else:
                output.append(normalize_token(token))
        while operators:
            output.append(operators.pop())

        stack: List[set[str]] = []
        for token in output:
            if token in precedence:
                if token == "NOT":
                    if not stack:
                        stack.append(set())
                    stack.append(universe - stack.pop())
                else:
                    right = stack.pop() if stack else set()
                    left = stack.pop() if stack else set()
                    stack.append(left & right if token == "AND" else left | right)
            else:
                stack.append(self.index.documents_for_term(token))
        return sorted(stack[-1]) if stack else []
