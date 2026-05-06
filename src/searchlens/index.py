"""Positional inverted index for SearchLens."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

from .preprocess import tokenize, tokenize_keep_stopwords


@dataclass(frozen=True)
class Document:
    """A document in the corpus."""

    doc_id: str
    title: str
    body: str
    url: str = ""
    category: str = ""
    tags: List[str] | None = None

    @property
    def text(self) -> str:
        return f"{self.title}. {self.body}"


class PositionalInvertedIndex:
    """A positional inverted index with enough statistics for ranked retrieval.

    postings[term][doc_id] is a list of token positions in that document.  The
    positions are based on tokenized full document text, including stopwords;
    scoring statistics use stopword-filtered normalized terms.
    """

    def __init__(self) -> None:
        self.documents: Dict[str, Document] = {}
        self.postings: Dict[str, Dict[str, List[int]]] = defaultdict(dict)
        self.term_freqs: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.doc_lengths: Dict[str, int] = {}
        self.doc_tokens: Dict[str, List[str]] = {}
        self.phrase_tokens: Dict[str, List[str]] = {}

    def __len__(self) -> int:
        return len(self.documents)

    @property
    def avg_doc_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)

    @property
    def vocabulary(self) -> List[str]:
        return sorted(self.postings.keys())

    def add_document(self, document: Document) -> None:
        if document.doc_id in self.documents:
            raise ValueError(f"Duplicate document id: {document.doc_id}")
        self.documents[document.doc_id] = document

        scoring_tokens = tokenize(document.text, remove_stopwords=True)
        phrase_tokens = tokenize_keep_stopwords(document.text)
        self.doc_tokens[document.doc_id] = scoring_tokens
        self.phrase_tokens[document.doc_id] = phrase_tokens
        self.doc_lengths[document.doc_id] = len(scoring_tokens)

        position_map: MutableMapping[str, List[int]] = defaultdict(list)
        for pos, token in enumerate(scoring_tokens):
            position_map[token].append(pos)
        for term, positions in position_map.items():
            self.postings[term][document.doc_id] = positions
            self.term_freqs[term][document.doc_id] = len(positions)

    @classmethod
    def build(cls, documents: Iterable[Document]) -> "PositionalInvertedIndex":
        index = cls()
        for doc in documents:
            index.add_document(doc)
        return index

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "PositionalInvertedIndex":
        documents: List[Document] = []
        with Path(path).open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON on line {line_number} of {path}") from exc
                documents.append(
                    Document(
                        doc_id=str(row["doc_id"]),
                        title=row.get("title", ""),
                        body=row.get("body", ""),
                        url=row.get("url", ""),
                        category=row.get("category", ""),
                        tags=list(row.get("tags", [])),
                    )
                )
        return cls.build(documents)

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, {}))

    def collection_frequency(self, term: str) -> int:
        return sum(self.term_freqs.get(term, {}).values())

    def term_frequency(self, doc_id: str, term: str) -> int:
        return self.term_freqs.get(term, {}).get(doc_id, 0)

    def documents_for_term(self, term: str) -> set[str]:
        return set(self.postings.get(term, {}).keys())

    def documents_for_terms(self, terms: Iterable[str]) -> set[str]:
        docs: set[str] = set()
        for term in terms:
            docs.update(self.documents_for_term(term))
        return docs

    def contains_phrase(self, doc_id: str, phrase_terms: List[str]) -> bool:
        """Return True when the normalized phrase occurs consecutively."""
        if not phrase_terms:
            return True
        tokens = self.phrase_tokens.get(doc_id, [])
        n = len(phrase_terms)
        if n > len(tokens):
            return False
        for i in range(len(tokens) - n + 1):
            if tokens[i : i + n] == phrase_terms:
                return True
        return False

    def top_terms(self, doc_id: str, limit: int = 10) -> List[tuple[str, int]]:
        counter = Counter(self.doc_tokens.get(doc_id, []))
        return counter.most_common(limit)

    def stats(self) -> Dict[str, float | int]:
        postings_count = sum(len(doc_map) for doc_map in self.postings.values())
        token_count = sum(self.doc_lengths.values())
        return {
            "documents": len(self.documents),
            "vocabulary": len(self.postings),
            "tokens": token_count,
            "avg_doc_length": round(self.avg_doc_length, 3),
            "postings": postings_count,
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "documents": {doc_id: asdict(doc) for doc_id, doc in self.documents.items()},
            "postings": {term: docs for term, docs in self.postings.items()},
            "term_freqs": {term: docs for term, docs in self.term_freqs.items()},
            "doc_lengths": self.doc_lengths,
            "doc_tokens": self.doc_tokens,
            "phrase_tokens": self.phrase_tokens,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "PositionalInvertedIndex":
        idx = cls()
        docs = data.get("documents", {})
        assert isinstance(docs, Mapping)
        for doc_id, row in docs.items():
            assert isinstance(row, Mapping)
            idx.documents[str(doc_id)] = Document(
                doc_id=str(row.get("doc_id", doc_id)),
                title=str(row.get("title", "")),
                body=str(row.get("body", "")),
                url=str(row.get("url", "")),
                category=str(row.get("category", "")),
                tags=list(row.get("tags", [])) if row.get("tags") is not None else [],
            )
        idx.postings = defaultdict(dict, {str(t): {str(d): list(p) for d, p in docs.items()} for t, docs in data.get("postings", {}).items()})  # type: ignore[union-attr]
        idx.term_freqs = defaultdict(dict, {str(t): {str(d): int(v) for d, v in docs.items()} for t, docs in data.get("term_freqs", {}).items()})  # type: ignore[union-attr]
        idx.doc_lengths = {str(k): int(v) for k, v in data.get("doc_lengths", {}).items()}  # type: ignore[union-attr]
        idx.doc_tokens = {str(k): list(v) for k, v in data.get("doc_tokens", {}).items()}  # type: ignore[union-attr]
        idx.phrase_tokens = {str(k): list(v) for k, v in data.get("phrase_tokens", {}).items()}  # type: ignore[union-attr]
        return idx

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "PositionalInvertedIndex":
        with Path(path).open("r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
