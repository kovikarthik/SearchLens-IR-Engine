"""Command line entry point for SearchLens."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .evaluate import evaluate_methods, load_qrels, load_queries
from .index import PositionalInvertedIndex
from .search import SearchEngine


def build_index(args: argparse.Namespace) -> None:
    index = PositionalInvertedIndex.from_jsonl(args.corpus)
    index.save(args.out)
    print(json.dumps(index.stats(), indent=2))


def run_search(args: argparse.Namespace) -> None:
    if args.index:
        index = PositionalInvertedIndex.load(args.index)
    else:
        index = PositionalInvertedIndex.from_jsonl(args.corpus)
    engine = SearchEngine(index)
    results = engine.search(args.query, method=args.method, top_k=args.top_k, pseudo_relevance=args.prf)
    for rank, result in enumerate(results, start=1):
        print(f"{rank:>2}. {result.doc_id}  {result.score:.4f}  {result.title}")
        print(f"    {result.snippet.replace('<mark>', '[').replace('</mark>', ']')}")


def run_eval(args: argparse.Namespace) -> None:
    index = PositionalInvertedIndex.from_jsonl(args.corpus)
    engine = SearchEngine(index)
    queries = load_queries(args.queries)
    qrels = load_qrels(args.qrels)
    results = evaluate_methods(engine, queries, qrels, args.methods, top_k=args.top_k)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.out).open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    print(json.dumps([r["aggregate"] | {"method": r["method"]} for r in results], indent=2))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SearchLens retrieval engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="Build and serialize an index")
    p_build.add_argument("--corpus", default="data/documents.jsonl")
    p_build.add_argument("--out", default="outputs/index.json")
    p_build.set_defaults(func=build_index)

    p_search = sub.add_parser("search", help="Run a ranked search")
    p_search.add_argument("--corpus", default="data/documents.jsonl")
    p_search.add_argument("--index", default="")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--method", choices=["bm25", "tfidf", "boolean"], default="bm25")
    p_search.add_argument("--top-k", type=int, default=10)
    p_search.add_argument("--prf", action="store_true", help="Enable pseudo relevance feedback for BM25")
    p_search.set_defaults(func=run_search)

    p_eval = sub.add_parser("evaluate", help="Evaluate retrieval methods")
    p_eval.add_argument("--corpus", default="data/documents.jsonl")
    p_eval.add_argument("--queries", default="data/queries.jsonl")
    p_eval.add_argument("--qrels", default="data/qrels.jsonl")
    p_eval.add_argument("--methods", nargs="+", default=["boolean", "tfidf", "bm25", "bm25_prf"])
    p_eval.add_argument("--top-k", type=int, default=10)
    p_eval.add_argument("--out", default="outputs/evaluation.json")
    p_eval.set_defaults(func=run_eval)
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = make_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
