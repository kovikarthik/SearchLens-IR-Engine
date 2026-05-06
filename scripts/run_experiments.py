"""Run SearchLens experiments and write reproducible outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from searchlens.evaluate import evaluate_methods, load_qrels, load_queries  # noqa: E402
from searchlens.index import PositionalInvertedIndex  # noqa: E402
from searchlens.search import SearchEngine  # noqa: E402

METHODS = ["boolean", "tfidf", "bm25", "bm25_prf"]


def main() -> None:
    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)

    index = PositionalInvertedIndex.from_jsonl(ROOT / "data" / "documents.jsonl")
    engine = SearchEngine(index)
    queries = load_queries(ROOT / "data" / "queries.jsonl")
    qrels = load_qrels(ROOT / "data" / "qrels.jsonl")

    index.save(out_dir / "index.json")
    results = evaluate_methods(engine, queries, qrels, METHODS, top_k=10)

    with (out_dir / "evaluation.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with (out_dir / "metrics.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "p5", "r10", "map", "mrr", "ndcg10"])
        writer.writeheader()
        for result in results:
            row = {"method": result["method"]}
            row.update(result["aggregate"])
            writer.writerow(row)

    with (out_dir / "sample_results.json").open("w", encoding="utf-8") as f:
        sample = {}
        for query in queries:
            sample[query["query_id"]] = {
                "query": query["text"],
                "bm25": [r.__dict__ for r in engine.search(query["text"], method="bm25", top_k=5)],
                "bm25_prf": [r.__dict__ for r in engine.search(query["text"], method="bm25", top_k=5, pseudo_relevance=True)],
            }
        json.dump(sample, f, indent=2)

    print(json.dumps({"index": index.stats(), "metrics": [r["aggregate"] | {"method": r["method"]} for r in results]}, indent=2))


if __name__ == "__main__":
    main()
