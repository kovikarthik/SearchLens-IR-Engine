"""Generate the self-contained Search Engine Technology corpus.

The corpus is intentionally synthetic but structured: each document is a short
technical note with one primary topic and optional secondary tags.  Relevance
judgments are generated from topic labels and then audited by hand through the
queries below.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def make_doc(doc_id: str, category: str, title: str, body: str, tags: List[str]) -> Dict[str, object]:
    return {
        "doc_id": doc_id,
        "title": title,
        "body": body,
        "category": category,
        "tags": tags,
        "url": f"https://example.edu/searchlens/{doc_id}",
    }


def documents() -> List[Dict[str, object]]:
    docs: List[Dict[str, object]] = []
    add = docs.append

    # Indexing and positional retrieval.
    add(make_doc("D001", "indexing", "Building an Inverted Index with Postings Lists", "An inverted index maps each normalized term to a postings list of documents. The pipeline tokenizes text, builds a term dictionary, records term frequency, and sorts document identifiers so query processing can intersect postings efficiently.", ["inverted index", "postings", "term frequency"]))
    add(make_doc("D002", "indexing", "Positional Postings for Phrase Search", "A positional index stores the exact token positions where a term occurs. Phrase queries such as information retrieval are answered by checking whether positions for adjacent terms appear consecutively in the same document.", ["positional postings", "phrase queries", "proximity"]))
    add(make_doc("D003", "indexing", "Tokenization and Term Normalization", "Index construction starts with tokenization, lowercasing, stopword filtering, and light stemming. These choices define the term vocabulary and determine whether queries like ranking and ranked retrieve the same documents.", ["tokenization", "normalization", "stemming"]))
    add(make_doc("D004", "indexing", "Dynamic Index Updates for Small Search Engines", "A small search engine can maintain an in-memory index and periodically write the dictionary and postings to disk. Dynamic updates add new documents, remove deleted identifiers, and rebuild summary statistics such as average document length.", ["dynamic indexing", "persistence", "average length"]))
    add(make_doc("D005", "indexing", "Query-Time Candidate Generation", "Candidate generation starts by taking the union or intersection of postings for query terms. A ranked retrieval engine then scores only candidate documents instead of scanning the entire corpus.", ["candidate generation", "postings", "ranking"]))

    # Boolean and phrase search.
    add(make_doc("D006", "boolean", "Boolean Retrieval with AND OR and NOT", "Boolean retrieval treats queries as set expressions over postings lists. AND computes an intersection, OR computes a union, and NOT subtracts a set from the document universe.", ["boolean", "set operations", "postings"]))
    add(make_doc("D007", "boolean", "Phrase Search as a Hard Filter", "A phrase search requires all quoted terms to occur in the specified order. SearchLens applies phrase constraints before scoring so a document must contain the exact phrase to be ranked.", ["phrase search", "positional index", "filtering"]))
    add(make_doc("D008", "boolean", "Proximity Matching Beyond Exact Phrases", "Proximity ranking rewards documents where query terms occur near each other. This can improve user satisfaction for verbose queries because related terms in the same passage usually signal topical relevance.", ["proximity", "ranking", "phrases"]))
    add(make_doc("D009", "boolean", "Limitations of Pure Boolean Search", "Pure Boolean search returns an unordered set, so users must inspect every matching document. Ranked retrieval addresses this limitation by ordering results with tf-idf, BM25, or other scoring functions.", ["boolean", "ranked retrieval", "tfidf", "bm25"]))
    add(make_doc("D010", "boolean", "Parsing User Queries into Search Operators", "A query parser recognizes parentheses and operators, normalizes ordinary terms, and builds an executable expression. Even a compact parser can support AND, OR, NOT, and simple precedence rules.", ["query parsing", "operators", "precedence"]))

    # BM25.
    add(make_doc("D011", "bm25", "BM25 Ranking with Term Frequency Saturation", "BM25 ranks documents by combining inverse document frequency with a saturated term frequency component. Repeating a query term helps at first, but the gain decreases so long documents do not dominate unfairly.", ["bm25", "term frequency", "idf", "saturation"]))
    add(make_doc("D012", "bm25", "Document Length Normalization in BM25", "The BM25 b parameter controls document length normalization. A higher value penalizes documents that are much longer than the collection average, while k1 controls the strength of term frequency saturation.", ["bm25", "length normalization", "k1", "b parameter"]))
    add(make_doc("D013", "bm25", "Why BM25 is a Strong Lexical Baseline", "BM25 is a durable lexical baseline because it is simple, efficient, and robust across many ad hoc retrieval collections. Modern hybrid systems often compare dense retrieval against BM25 before adding reranking.", ["bm25", "lexical retrieval", "hybrid", "baseline"]))
    add(make_doc("D014", "bm25", "BM25 Implementation Notes", "A practical BM25 implementation needs document frequency, document length, average length, and term frequency statistics. Scores can be computed over a candidate set from the inverted index.", ["bm25", "implementation", "statistics"]))
    add(make_doc("D015", "bm25", "BM25 Failure Cases", "Lexical BM25 may miss relevant documents that use different vocabulary from the query. Query expansion, thesauri, dense retrieval, or user feedback can reduce this vocabulary mismatch problem.", ["bm25", "vocabulary mismatch", "query expansion"]))

    # TF-IDF and vector space.
    add(make_doc("D016", "tfidf", "Vector Space Ranking with TF-IDF", "The vector space model represents documents and queries as weighted term vectors. TF-IDF combines term frequency with inverse document frequency, and cosine similarity compares the angle between vectors.", ["tfidf", "vector space", "cosine similarity"]))
    add(make_doc("D017", "tfidf", "Inverse Document Frequency and Specificity", "Inverse document frequency assigns higher weights to terms that occur in fewer documents. Specific terms help discriminate relevant documents, while very common terms contribute less to ranking.", ["idf", "term specificity", "ranking"]))
    add(make_doc("D018", "tfidf", "Cosine Normalization for Different Document Lengths", "Cosine normalization divides by vector length so longer documents do not automatically receive higher scores. This is useful when corpus documents vary in length and verbosity.", ["cosine", "normalization", "document length"]))
    add(make_doc("D019", "tfidf", "Comparing TF-IDF and BM25", "TF-IDF cosine and BM25 are both lexical ranking models. BM25 adds saturation and length normalization, while tf-idf cosine offers a simple geometric interpretation.", ["tfidf", "bm25", "comparison"]))
    add(make_doc("D020", "tfidf", "Term Weighting in a Complete Search System", "A complete scoring system often starts with tf-idf term weighting, candidate generation, and efficient top-k ranking. Engineering decisions determine latency, memory use, and reproducibility.", ["term weighting", "top k", "efficiency"]))

    # Web crawling.
    add(make_doc("D021", "crawling", "Crawler Politeness and Robots Exclusion", "A web crawler should respect robots.txt, throttle requests to each host, and avoid overloading servers. Politeness policies are essential for responsible collection of web pages.", ["crawler", "robots", "politeness"]))
    add(make_doc("D022", "crawling", "URL Frontier Scheduling", "The URL frontier stores discovered links and selects the next page to fetch. Good scheduling balances freshness, host politeness, priority, and coverage of important pages.", ["crawler", "url frontier", "scheduling"]))
    add(make_doc("D023", "crawling", "Duplicate and Near-Duplicate Detection", "Crawlers often encounter mirrored pages and repeated templates. Fingerprinting and shingling can detect near duplicates before they waste index space and distort retrieval evaluation.", ["duplicate detection", "shingling", "crawler"]))
    add(make_doc("D024", "crawling", "Parsing HTML into Indexable Text", "A crawler must extract readable text from HTML, remove boilerplate navigation, preserve useful anchor text, and pass clean content to the indexing pipeline.", ["html parsing", "anchor text", "indexing"]))
    add(make_doc("D025", "crawling", "Freshness in Incremental Crawling", "Incremental crawling revisits pages according to expected change frequency. Freshness is especially important for news, prices, schedules, and other dynamic search collections.", ["freshness", "incremental crawling", "web search"]))

    # Link analysis / PageRank.
    add(make_doc("D026", "pagerank", "PageRank and the Random Surfer Model", "PageRank models a random surfer following links with occasional teleportation. A page receives high score when many important pages link to it.", ["pagerank", "link analysis", "random surfer"]))
    add(make_doc("D027", "pagerank", "Combining Link Analysis with Text Ranking", "Web search systems can combine content relevance from BM25 with link authority from PageRank. The combined score improves ranking when anchor text and links indicate popularity or trust.", ["pagerank", "bm25", "hybrid scoring"]))
    add(make_doc("D028", "pagerank", "Anchor Text as External Evidence", "Anchor text often describes the destination page using words chosen by other authors. Indexing anchor text can improve retrieval for pages whose own content lacks the query terms.", ["anchor text", "link analysis", "web search"]))
    add(make_doc("D029", "pagerank", "Topic-Sensitive Link Ranking", "Topic-sensitive PageRank computes authority within topical subsets. It can help distinguish pages about search engines from pages about unrelated popular subjects.", ["topic-sensitive pagerank", "authority", "ranking"]))
    add(make_doc("D030", "pagerank", "Link Spam and Authority Manipulation", "Link-based ranking can be manipulated by link farms and spam networks. Robust systems monitor suspicious link patterns and combine authority with content quality signals.", ["link spam", "pagerank", "robustness"]))

    # Spelling correction.
    add(make_doc("D031", "spelling", "Edit Distance for Spelling Correction", "Spelling correction ranks candidate terms by edit distance from the misspelled query term. Insertions, deletions, substitutions, and transpositions approximate the effort needed to fix a word.", ["spelling", "edit distance", "candidate terms"]))
    add(make_doc("D032", "spelling", "K-Gram Indexes for Tolerant Retrieval", "A k-gram index stores character n-grams for each vocabulary term. It generates candidates for wildcard queries and spelling correction before edit distance reranking.", ["k gram", "wildcard", "spelling"]))
    add(make_doc("D033", "spelling", "Noisy Channel Ranking for Corrections", "A noisy channel spelling model combines the likelihood of an observed typo with the prior probability of the intended term. Frequent vocabulary terms receive more confidence after candidate generation.", ["noisy channel", "spelling", "term prior"]))
    add(make_doc("D034", "spelling", "Context-Sensitive Query Correction", "Context-sensitive correction uses surrounding query words to choose among valid alternatives. For example, search engine technolgy should become search engine technology rather than a different rare word.", ["context", "spelling", "query correction"]))
    add(make_doc("D035", "spelling", "When Not to Correct a Query", "A search system should avoid aggressive correction for names, acronyms, and technical terms such as BM25 or nDCG. Showing a suggestion is safer than silently rewriting a specialized query.", ["spelling", "acronyms", "user interface"]))

    # Query expansion / feedback.
    add(make_doc("D036", "expansion", "Rocchio Relevance Feedback", "Rocchio feedback moves a query vector toward relevant documents and away from nonrelevant documents. It is a classic method for improving vector space retrieval when relevance judgments are available.", ["rocchio", "relevance feedback", "vector space"]))
    add(make_doc("D037", "expansion", "Pseudo Relevance Feedback without User Labels", "Pseudo relevance feedback assumes the top-ranked documents from an initial search are relevant. Expansion terms are selected from those documents and appended to the query.", ["pseudo relevance feedback", "query expansion", "bm25"]))
    add(make_doc("D038", "expansion", "Thesaurus-Based Query Expansion", "A thesaurus can add synonyms and related concepts to a query. This helps with vocabulary mismatch but can reduce precision if broad terms introduce topic drift.", ["thesaurus", "query expansion", "vocabulary mismatch"]))
    add(make_doc("D039", "expansion", "Term Selection for Feedback", "Feedback term selection favors high-idf terms that occur frequently in top documents. Filtering stopwords and original query terms keeps expansion concise.", ["term selection", "idf", "feedback"]))
    add(make_doc("D040", "expansion", "Risks of Topic Drift", "Query expansion can drift when the first-pass results include nonrelevant documents. Conservative feedback depth and a small number of expansion terms reduce the risk.", ["topic drift", "query expansion", "evaluation"]))

    # Evaluation.
    add(make_doc("D041", "evaluation", "Precision Recall and F-Measure", "Evaluation begins by comparing retrieved documents with relevance judgments. Precision measures the fraction of retrieved documents that are relevant, while recall measures coverage of all relevant documents.", ["precision", "recall", "relevance judgments"]))
    add(make_doc("D042", "evaluation", "Mean Average Precision", "Mean average precision summarizes the precision observed at every rank where a relevant document appears. MAP rewards systems that retrieve relevant documents early and consistently.", ["map", "average precision", "ranked retrieval"]))
    add(make_doc("D043", "evaluation", "nDCG for Graded Relevance", "Normalized discounted cumulative gain evaluates ranked lists with graded relevance. Highly relevant documents receive larger gain, and the discount factor rewards early ranks.", ["ndcg", "graded relevance", "discount"]))
    add(make_doc("D044", "evaluation", "TREC-Style Test Collections", "A test collection contains a corpus, topics, relevance judgments, and evaluation metrics. This structure supports reproducible comparison among retrieval models.", ["test collection", "trec", "reproducibility"]))
    add(make_doc("D045", "evaluation", "Limitations of Offline Evaluation", "Offline metrics may not capture user satisfaction, presentation quality, or interactive search behavior. A deployed system should combine test collection results with user-centered evaluation.", ["user satisfaction", "limitations", "metrics"]))

    # Compression.
    add(make_doc("D046", "compression", "Variable Byte Encoding for Postings", "Variable byte encoding stores small gaps with fewer bytes. Search engines gap-encode sorted document identifiers before compression to reduce postings list size.", ["variable byte", "gap encoding", "postings compression"]))
    add(make_doc("D047", "compression", "Gamma Codes and Integer Compression", "Gamma codes encode positive integers using a unary length and binary offset. They are useful for compact postings but require bit-level processing.", ["gamma code", "integer compression", "postings"]))
    add(make_doc("D048", "compression", "Skip Pointers for Faster Intersections", "Skip pointers accelerate postings intersection by allowing query processing to jump over blocks that cannot contain a match. They trade extra storage for faster Boolean evaluation.", ["skip pointers", "postings intersection", "boolean"]))
    add(make_doc("D049", "compression", "Dictionary Compression", "The term dictionary can be compressed with blocked storage and front coding. Compression improves memory locality for large vocabularies.", ["dictionary compression", "front coding", "vocabulary"]))
    add(make_doc("D050", "compression", "Compression Trade-Offs in Search Engines", "Index compression reduces disk and memory footprint but increases decoding cost. Practical systems balance latency, storage, and implementation complexity.", ["compression", "latency", "storage"]))

    # Neural and hybrid retrieval.
    add(make_doc("D051", "neural", "Dense Retrieval with Learned Embeddings", "Dense retrieval encodes queries and documents into continuous vectors. Approximate nearest neighbor search retrieves semantically similar documents even when exact query terms are absent.", ["dense retrieval", "embeddings", "semantic search"]))
    add(make_doc("D052", "neural", "Hybrid Lexical and Dense Retrieval", "Hybrid retrieval combines BM25 lexical scores with dense vector similarity. The lexical component preserves exact matching, while dense retrieval can address synonymy and paraphrases.", ["hybrid", "bm25", "dense retrieval"]))
    add(make_doc("D053", "neural", "Cross-Encoder Reranking", "A cross-encoder reranker reads the query and document together to estimate relevance. It is often more accurate than first-stage retrieval but too expensive to run over the whole corpus.", ["reranking", "cross encoder", "latency"]))
    add(make_doc("D054", "neural", "Retrieval-Augmented Generation", "Retrieval-augmented generation uses a search component to supply evidence to a language model. The quality of retrieved passages directly affects answer faithfulness.", ["rag", "retrieval augmented generation", "evidence"]))
    add(make_doc("D055", "neural", "Evaluating Dense Retrieval Against BM25", "Dense systems should be compared with BM25 baselines on the same queries and relevance judgments. Without a lexical baseline, semantic retrieval improvements are hard to interpret.", ["dense retrieval", "bm25", "evaluation"]))

    # Spam, security, and robustness.
    add(make_doc("D056", "robustness", "Search Spam and Keyword Stuffing", "Search spam attempts to manipulate ranking by repeating popular terms, hiding text, or creating low-quality pages. Robust ranking should detect unnatural term distributions.", ["search spam", "keyword stuffing", "robustness"]))
    add(make_doc("D057", "robustness", "Adversarial Documents in Retrieval", "Adversarial documents can exploit lexical matchers by including many query terms without satisfying the information need. Evaluation should include difficult negative examples.", ["adversarial", "lexical matching", "negative examples"]))
    add(make_doc("D058", "robustness", "Trust Signals for Web Search", "Trust signals include domain reputation, link quality, author information, and content consistency. They complement textual relevance in open web environments.", ["trust", "web search", "content quality"]))
    add(make_doc("D059", "robustness", "Bias and Fairness in Ranking", "Ranking systems can amplify exposure disparities when popular documents receive more clicks and authority. Fairness-aware evaluation studies whether different groups receive equitable visibility.", ["fairness", "ranking", "exposure"]))
    add(make_doc("D060", "robustness", "Robust Evaluation of Search Systems", "Robust retrieval evaluation tests performance under misspellings, spam, ambiguous queries, and distribution shift. Stress tests reveal limitations not visible in easy benchmark topics.", ["robust evaluation", "spam", "ambiguity"]))

    return docs


QUERIES = [
    {"query_id": "Q01", "text": "inverted index postings positions phrase query", "topic": "indexing"},
    {"query_id": "Q02", "text": "bm25 term frequency document length normalization", "topic": "bm25"},
    {"query_id": "Q03", "text": "tf idf cosine vector space retrieval", "topic": "tfidf"},
    {"query_id": "Q04", "text": "boolean AND OR NOT phrase proximity", "topic": "boolean"},
    {"query_id": "Q05", "text": "pagerank link analysis random surfer anchor text", "topic": "pagerank"},
    {"query_id": "Q06", "text": "crawler robots politeness url frontier duplicate detection", "topic": "crawling"},
    {"query_id": "Q07", "text": "spelling correction k gram edit distance typo", "topic": "spelling"},
    {"query_id": "Q08", "text": "pseudo relevance feedback rocchio query expansion", "topic": "expansion"},
    {"query_id": "Q09", "text": "precision recall map ndcg evaluation metrics", "topic": "evaluation"},
    {"query_id": "Q10", "text": "index compression variable byte gamma skip pointers", "topic": "compression"},
    {"query_id": "Q11", "text": "dense retrieval hybrid bm25 reranking embeddings", "topic": "neural"},
    {"query_id": "Q12", "text": "search spam adversarial ranking robustness", "topic": "robustness"},
]

RELATED = {
    "Q01": ["D007", "D048"],
    "Q02": ["D019", "D052"],
    "Q03": ["D036", "D020"],
    "Q04": ["D002", "D048"],
    "Q05": ["D024", "D030"],
    "Q06": ["D024", "D025"],
    "Q07": ["D032", "D034"],
    "Q08": ["D015", "D038"],
    "Q09": ["D040", "D055", "D060"],
    "Q10": ["D001", "D048"],
    "Q11": ["D013", "D055"],
    "Q12": ["D030", "D060"],
}


def qrels(docs: List[Dict[str, object]]) -> List[Dict[str, object]]:
    by_category: Dict[str, List[str]] = {}
    for doc in docs:
        by_category.setdefault(str(doc["category"]), []).append(str(doc["doc_id"]))
    out: List[Dict[str, object]] = []
    for q in QUERIES:
        qid = q["query_id"]
        topic = q["topic"]
        for doc_id in by_category[topic]:
            out.append({"query_id": qid, "doc_id": doc_id, "relevance": 2})
        for doc_id in RELATED.get(qid, []):
            out.append({"query_id": qid, "doc_id": doc_id, "relevance": 1})
    # De-duplicate by taking max relevance.
    merged: Dict[tuple[str, str], int] = {}
    for row in out:
        key = (str(row["query_id"]), str(row["doc_id"]))
        merged[key] = max(merged.get(key, 0), int(row["relevance"]))
    return [
        {"query_id": qid, "doc_id": doc_id, "relevance": rel}
        for (qid, doc_id), rel in sorted(merged.items())
    ]


def write_jsonl(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    docs = documents()
    write_jsonl(DATA / "documents.jsonl", docs)
    write_jsonl(DATA / "queries.jsonl", QUERIES)
    write_jsonl(DATA / "qrels.jsonl", qrels(docs))
    print(f"Wrote {len(docs)} documents, {len(QUERIES)} queries, and {len(qrels(docs))} qrels to {DATA}")


if __name__ == "__main__":
    main()
