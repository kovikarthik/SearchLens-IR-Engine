"""Evaluation metrics for ranked retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .search import SearchEngine

Qrels = Dict[str, Dict[str, int]]
Queries = List[Dict[str, str]]


def load_queries(path: str | Path) -> Queries:
    rows: Queries = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_qrels(path: str | Path) -> Qrels:
    qrels: Qrels = {}
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            qrels.setdefault(str(row["query_id"]), {})[str(row["doc_id"])] = int(row.get("relevance", 1))
    return qrels


def precision_at_k(ranked: Sequence[str], relevant: Mapping[str, int], k: int, rel_threshold: int = 1) -> float:
    if k <= 0:
        return 0.0
    rel = {doc_id for doc_id, grade in relevant.items() if grade >= rel_threshold}
    return sum(1 for doc_id in ranked[:k] if doc_id in rel) / k


def recall_at_k(ranked: Sequence[str], relevant: Mapping[str, int], k: int, rel_threshold: int = 1) -> float:
    rel = {doc_id for doc_id, grade in relevant.items() if grade >= rel_threshold}
    if not rel:
        return 0.0
    return sum(1 for doc_id in ranked[:k] if doc_id in rel) / len(rel)


def average_precision(ranked: Sequence[str], relevant: Mapping[str, int], rel_threshold: int = 1) -> float:
    rel = {doc_id for doc_id, grade in relevant.items() if grade >= rel_threshold}
    if not rel:
        return 0.0
    hits = 0
    total = 0.0
    for i, doc_id in enumerate(ranked, start=1):
        if doc_id in rel:
            hits += 1
            total += hits / i
    return total / len(rel)


def reciprocal_rank(ranked: Sequence[str], relevant: Mapping[str, int], rel_threshold: int = 1) -> float:
    rel = {doc_id for doc_id, grade in relevant.items() if grade >= rel_threshold}
    for i, doc_id in enumerate(ranked, start=1):
        if doc_id in rel:
            return 1.0 / i
    return 0.0


def dcg_at_k(ranked: Sequence[str], relevant: Mapping[str, int], k: int) -> float:
    import math

    score = 0.0
    for i, doc_id in enumerate(ranked[:k], start=1):
        gain = relevant.get(doc_id, 0)
        if gain > 0:
            score += (2**gain - 1) / math.log2(i + 1)
    return score


def ndcg_at_k(ranked: Sequence[str], relevant: Mapping[str, int], k: int) -> float:
    ideal = sorted(relevant.values(), reverse=True)
    ideal_ranked = [f"ideal-{i}" for i in range(len(ideal))]
    ideal_rel = {doc_id: grade for doc_id, grade in zip(ideal_ranked, ideal)}
    denom = dcg_at_k(ideal_ranked, ideal_rel, k)
    if denom == 0:
        return 0.0
    return dcg_at_k(ranked, relevant, k) / denom


def evaluate_method(engine: SearchEngine, queries: Queries, qrels: Qrels, method: str, top_k: int = 10) -> Dict[str, object]:
    per_query: Dict[str, Dict[str, float | List[str]]] = {}
    totals = {"p5": 0.0, "r10": 0.0, "map": 0.0, "mrr": 0.0, "ndcg10": 0.0}
    for query in queries:
        qid = str(query["query_id"])
        text = str(query["text"])
        pseudo = method.endswith("_prf")
        base_method = method.replace("_prf", "")
        results = engine.search(text, method=base_method, top_k=top_k, pseudo_relevance=pseudo)
        ranked = [result.doc_id for result in results]
        rel = qrels.get(qid, {})
        metrics = {
            "p5": precision_at_k(ranked, rel, 5),
            "r10": recall_at_k(ranked, rel, 10),
            "map": average_precision(ranked, rel),
            "mrr": reciprocal_rank(ranked, rel),
            "ndcg10": ndcg_at_k(ranked, rel, 10),
            "ranked": ranked,
        }
        per_query[qid] = metrics
        for key in totals:
            totals[key] += float(metrics[key])
    n = max(len(queries), 1)
    aggregate = {key: round(value / n, 4) for key, value in totals.items()}
    return {"method": method, "aggregate": aggregate, "per_query": per_query}


def evaluate_methods(engine: SearchEngine, queries: Queries, qrels: Qrels, methods: Sequence[str], top_k: int = 10) -> List[Dict[str, object]]:
    return [evaluate_method(engine, queries, qrels, method, top_k=top_k) for method in methods]


if __name__ == "__main__":
    import argparse
    from .index import PositionalInvertedIndex

    parser = argparse.ArgumentParser(description="Evaluate SearchLens retrieval models")
    parser.add_argument("--index", default="data/documents.jsonl", help="Path to documents JSONL")
    parser.add_argument("--queries", default="data/queries.jsonl", help="Path to queries JSONL")
    parser.add_argument("--qrels", default="data/qrels.jsonl", help="Path to relevance judgments")
    parser.add_argument("--methods", nargs="+", default=["boolean", "tfidf", "bm25", "bm25_prf"])
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    idx = PositionalInvertedIndex.from_jsonl(root / args.index)
    engine = SearchEngine(idx)
    queries = load_queries(root / args.queries)
    qrels = load_qrels(root / args.qrels)

    results = evaluate_methods(engine, queries, qrels, args.methods)
    print(f"{'Method':<15} | {'P@5':<6} | {'R@10':<6} | {'MAP':<6} | {'MRR':<6} | {'nDCG@10':<6}")
    print("-" * 65)
    for res in results:
        m = res["method"]
        a = res["aggregate"]
        print(f"{m:<15} | {a['p5']:<6} | {a['r10']:<6} | {a['map']:<6} | {a['mrr']:<6} | {a['ndcg10']:<6}")
