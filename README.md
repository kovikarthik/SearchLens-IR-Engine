# SearchLens: Classical Search Engine with BM25 and Feedback

SearchLens is a high-performance, zero-dependency information retrieval system built for **CECS 429/529: Search Engine Technology**. It provides a full-stack IR implementation, from a positional inverted index to a premium web-based executive portal.

## ✨ Key Features
- 🚀 **Zero-Dependency Engine**: Built entirely with the Python standard library for maximum portability.
- 📊 **State-of-the-Art Ranking**: Supports **BM25 Probabilistic Ranking**, TF-IDF Vector Space Model, and Boolean Overlap.
- 🧠 **Feedback Intelligence**: Conservative Pseudo-Relevance Feedback (PRF) for automated query expansion.
- 🔍 **Phrase Search**: High-precision phrase query support via positional indexing.
- 🖥️ **Executive Portal**: Modern, responsive web UI with real-time **Ranking Intelligence** (search explanations) and latency tracking.
- 📈 **Evaluation Harness**: Automated calculation of MAP, nDCG, MRR, P@5, and Recall@10.
- 🐳 **Docker-Ready**: One-command production deployment via Docker Compose.

## Target Venue
This project is framed as a system demonstration for the **ACM SIGIR Conference on Research and Development in Information Retrieval**. It emphasizes engineering excellence, mathematical rigor, and UI/UX for IR systems.

## Repository contents

```text
src/searchlens/              Core implementation
scripts/create_synthetic_corpus.py
scripts/run_experiments.py   Rebuilds index and evaluation outputs
data/                        Synthetic corpus, queries, and qrels
outputs/                     Index, metrics, and sample search results
paper/                       ACM-style final report source and PDF
slides/                      Presentation deck
web/app.py                   Local web demo, no external framework required
tests/                       Unit tests
```

## Quick start

The project uses only the Python standard library.

```bash
python --version  # Python 3.10 or newer recommended
python scripts/create_synthetic_corpus.py
PYTHONPATH=src python scripts/run_experiments.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Search examples

```bash
PYTHONPATH=src python -m searchlens.cli search --query "bm25 document length normalization" --method bm25 --top-k 5
PYTHONPATH=src python -m searchlens.cli search --query '"information retrieval" phrase' --method bm25 --top-k 5
PYTHONPATH=src python -m searchlens.cli search --query "pseudo relevance feedback" --method bm25 --prf --top-k 5
```

## Evaluation

```bash
PYTHONPATH=src python -m searchlens.cli evaluate \
  --corpus data/documents.jsonl \
  --queries data/queries.jsonl \
  --qrels data/qrels.jsonl \
  --out outputs/evaluation.json
```

The reproduced aggregate metrics are written to `outputs/metrics.csv`.

| Method | P@5 | Recall@10 | MAP | MRR | nDCG@10 |
|---|---:|---:|---:|---:|---:|
| Boolean overlap | 0.8333 | 0.8216 | 0.7736 | 1.0000 | 0.8487 |
| TF-IDF cosine | 0.8667 | 0.8593 | 0.8242 | 1.0000 | 0.8842 |
| BM25 | 0.8833 | 0.8593 | 0.8276 | 1.0000 | 0.8851 |
| BM25 + PRF | 0.8667 | 0.8641 | 0.8166 | 1.0000 | 0.8815 |

## Local web demo

```bash
PYTHONPATH=src python web/app.py
```

Then open the printed local URL in a browser.  The app supports BM25, TF-IDF, Boolean-overlap ranking, phrase queries, and optional pseudo-relevance feedback.

## 🚀 Production Deployment

SearchLens is production-ready and can be deployed using Docker:

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```
The app will be available at `http://localhost:8000`.

### Manual Deployment
1. Install dependencies (none required for core, but `pip install` any third-party if added).
2. Set PYTHONPATH: `export PYTHONPATH=src`
3. Run: `python web/app.py --host 0.0.0.0 --port 8000`

## 📊 Project Structure
- `src/searchlens/`: Core engine logic (Indexing, Search, Preprocessing).
- `data/`: Sample SETC-60 technical collection.
- `web/`: Modern, responsive search portal.
- `paper/`: SIGIR-style academic report.
- `slides/`: Professional presentation generator.

## Academic integrity note

Before final submission, replace placeholder author information in the paper and slides with your own name and student details.  The implementation, results, and paper are designed to be transparent and reproducible.
