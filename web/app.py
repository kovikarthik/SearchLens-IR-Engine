"""Premium local web demo for SearchLens using only the Python standard library."""

from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import os
import sys
from urllib.parse import parse_qs, urlparse
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from searchlens.index import PositionalInvertedIndex
from searchlens.search import SearchEngine

# Initialize core engine
INDEX = PositionalInvertedIndex.from_jsonl(ROOT / "data" / "documents.jsonl")
ENGINE = SearchEngine(INDEX)

# --- PREMIUM CSS SYSTEM ---
CSS = """
:root {
    --primary: #156082;
    --primary-dark: #0d4a66;
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
}

* { box-sizing: border-box; transition: all 0.2s ease; }

body { 
    font-family: 'Outfit', 'Inter', system-ui, sans-serif; 
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    line-height: 1.6;
}

header { 
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    padding: 4rem 1rem;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

header h1 { margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -0.025em; }
header p { opacity: 0.9; margin-top: 0.75rem; font-size: 1.25rem; }

main { max-width: 1000px; margin: -3rem auto 5rem; padding: 0 1rem; }

.search-card {
    background: var(--card);
    padding: 2.5rem;
    border-radius: 1.5rem;
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

.form-group { display: flex; gap: 1rem; align-items: stretch; margin-bottom: 2rem; }

input[type=text] { 
    flex: 1;
    padding: 1rem 1.5rem;
    border: 2px solid var(--border);
    border-radius: 1rem;
    font-size: 1.1rem;
    outline: none;
}

input[type=text]:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(21, 96, 130, 0.1); }

select, button { 
    padding: 1rem 2rem;
    border-radius: 1rem;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    border: none;
}

select { background: #f1f5f9; border: 2px solid var(--border); appearance: none; }

button { background: var(--primary); color: white; }
button:hover { background: var(--primary-dark); transform: translateY(-2px); }

.filters { display: flex; gap: 2rem; align-items: center; font-size: 0.95rem; color: var(--text-muted); }
.filters label { cursor: pointer; display: flex; align-items: center; gap: 0.6rem; font-weight: 600; }

.stats-bar { margin: 3rem 0 1.5rem; font-size: 0.9rem; color: var(--text-muted); display: flex; justify-content: space-between; font-weight: 500; }

.result-item {
    background: var(--card);
    padding: 2rem;
    border-radius: 1.25rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
}

.result-item:hover { border-color: var(--primary); box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05); }

.result-meta { display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.8rem; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-bottom: 1rem; align-items: center; }
.result-title { margin: 0 0 0.75rem; font-size: 1.5rem; font-weight: 800; color: #0f172a; }
.result-snippet { color: #475569; font-size: 1.05rem; margin-bottom: 1.5rem; }
.result-explanation { background: #f8fafc; padding: 1rem; border-radius: 0.75rem; font-size: 0.9rem; border-left: 5px solid var(--border); color: #64748b; }

mark { background: #fef08a; padding: 0 3px; border-radius: 4px; color: #854d0e; font-weight: 600; }

.badge { background: #e0f2fe; color: #0369a1; padding: 0.35rem 1rem; border-radius: 2rem; font-size: 0.8rem; }

.examples-tray { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.5rem; }
.example-chip { 
    background: #f1f5f9; 
    color: var(--text-muted); 
    padding: 0.5rem 1rem; 
    border-radius: 0.75rem; 
    text-decoration: none; 
    font-size: 0.9rem; 
    font-weight: 600;
}
.example-chip:hover { background: var(--primary); color: white; }

footer { text-align: center; padding: 4rem 2rem; color: var(--text-muted); font-size: 0.9rem; border-top: 1px solid var(--border); margin-top: 5rem; }

@media (max-width: 768px) {
    .form-group { flex-direction: column; }
    header h1 { font-size: 2.25rem; }
}
"""

def page(q: str = "", method: str = "bm25", prf: bool = False) -> str:
    safe_q = html.escape(q)
    checked = "checked" if prf else ""
    method_options = "".join(
        f'<option value="{m}" {"selected" if m == method else ""}>{label}</option>'
        for m, label in [("bm25", "BM25 Probabilistic"), ("tfidf", "TF-IDF Vector Space"), ("boolean", "Boolean Overlap")]
    )
    
    results_html = ""
    res_count = 0
    latency = 0.0
    if q.strip():
        start = time.time()
        results = ENGINE.search(q, method=method, top_k=10, pseudo_relevance=prf and method == "bm25")
        latency = (time.time() - start) * 1000
        res_count = len(results)
        if not results:
            results_html = '<div class="result-item" style="text-align:center; padding: 4rem;"><h3>No matches found.</h3><p>Try broadening your search or checking for typos.</p></div>'
        else:
            cards = []
            for rank, res in enumerate(results, start=1):
                cards.append(f"""
                    <div class="result-item">
                      <div class="result-meta">
                        <span>Rank {rank}</span>
                        <span style="color:#cbd5e1">&bull;</span>
                        <span>Doc: {res.doc_id}</span>
                        <span style="color:#cbd5e1">&bull;</span>
                        <span>Score: {res.score:.4f}</span>
                        <span class="badge">{html.escape(res.category)}</span>
                      </div>
                      <h3 class="result-title">{html.escape(res.title)}</h3>
                      <p class="result-snippet">{res.snippet}</p>
                      <div class="result-explanation"><strong>Ranking Intelligence:</strong> {html.escape(res.explanation)}</div>
                    </div>
                """)
            results_html = "\n".join(cards)
            
    examples = [
        "bm25 document length normalization",
        "inverted index postings positions",
        "pseudo relevance feedback rocchio",
        '"information retrieval" phrase',
    ]
    example_links = "".join(
        f'<a href="/search?q={html.escape(e)}&method=bm25" class="example-chip">{html.escape(e)}</a>' for e in examples
    )
    
    stats = INDEX.stats()
    # FIXED: Using correct keys 'vocabulary' and 'postings' as per index.py
    stats_str = f"Indexed {stats['documents']} documents with {stats['vocabulary']} unique terms across {stats['postings']} postings."

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SearchLens | Professional IR System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@400;700;800&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
  <header>
    <h1>SearchLens</h1>
    <p>High-Performance Classical Search Engine</p>
  </header>
  
  <main>
    <div class="search-card">
      <form action="/search" method="get">
        <div class="form-group">
          <input type="text" name="q" value="{safe_q}" placeholder="Ask a technical question..." autofocus>
          <select name="method">{method_options}</select>
          <button type="submit">Execute Search</button>
        </div>
        <div class="filters">
          <label><input type="checkbox" name="prf" value="1" {checked}> Apply Pseudo-Relevance Feedback (PRF)</label>
          <div style="flex:1"></div>
          <div class="examples-tray">
            {example_links}
          </div>
        </div>
      </form>
    </div>

    <div class="stats-bar">
      <span>{stats_str}</span>
      <span>{f'Found {res_count} results in {latency:.2f}ms' if q else ''}</span>
    </div>

    <div id="results">
      {results_html}
    </div>
  </main>
  
  <footer>
    <p>&copy; 2026 SearchLens Project Team</p>
    <p style="margin-top:0.5rem; font-weight:700">Mohit Krishna Emani | Karthik Kovi | Vignan Gadaley | Ram Vadlamudi</p>
    <p style="font-size:0.8rem; margin-top:1rem">California State University, Long Beach | Search Engine Technology</p>
  </footer>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/search"}:
            self.send_error(404)
            return
        params = parse_qs(parsed.query)
        q = params.get("q", [""])[0]
        method = params.get("method", ["bm25"])[0]
        if method not in {"bm25", "tfidf", "boolean"}:
            method = "bm25"
        prf = params.get("prf", [""])[0] == "1"
        body = page(q=q, method=method, prf=prf).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        pass # Production clean

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SearchLens web portal")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=int(os.environ.get("PORT", 8000)), type=int)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), Handler)
    print(f"--- SearchLens Executive Portal ---")
    print(f"URL: http://{args.host}:{args.port}/")
    print(f"Status: OPERATIONAL")
    server.serve_forever()

if __name__ == "__main__":
    main()
