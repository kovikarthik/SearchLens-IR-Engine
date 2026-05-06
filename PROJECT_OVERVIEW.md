# Project SearchLens: Comprehensive Overview

This document serves as a complete study guide and technical overview for the **SearchLens** project. Use this to prepare for your presentation and to answer technical questions from your professor.

---

## 1. Project Goal & Motivation
**Goal:** To build a transparent, reproducible classical search engine that demonstrates the core principles of Information Retrieval (IR) without relying on "black-box" libraries.

**Why it matters:**
*   Modern search engines are complex, but they all rely on these fundamental building blocks: indexing, ranking, and feedback.
*   The project compares different mathematical models (TF-IDF vs. BM25) to prove which one works best on a controlled technical dataset.

---

## 2. Technical Architecture (The Pipeline)
The engine follows a standard IR pipeline:
1.  **Preprocessing:** Cleans the text (lowercasing, removing "stopwords" like 'the' or 'is', and light normalization).
2.  **Indexing:** Builds a **Positional Inverted Index**. Unlike a simple index, this stores the *location* of each word, which is what allows the engine to support **Phrase Searches** (e.g., searching for `"machine learning"` as a specific unit).
3.  **Candidate Generation:** When you type a query, the engine quickly finds all documents that contain at least one of your words.
4.  **Ranking:** The engine applies a mathematical formula to score each document and sort them from most relevant to least relevant.
5.  **Snippets:** The engine generates short text previews with your search terms highlighted.

---

## 3. Retrieval Models (The "Math")
You implemented three models. You should be able to explain the difference:

| Model | How it Works | Pros/Cons |
| :--- | :--- | :--- |
| **Boolean Overlap** | Counts how many unique query terms are in the doc. | Very simple, but doesn't care about word importance. |
| **TF-IDF Cosine** | Weights rare words higher and normalizes by document length. | Classic and effective, but can be "fooled" by word repetition. |
| **BM25** | A sophisticated probabilistic model with "saturation." | **The Best.** It realizes that seeing a word 20 times isn't 20x better than seeing it once. |

---

## 4. Advanced Feature: Pseudo-Relevance Feedback (PRF)
**What it is:** A way for the search engine to "think" for the user.
1.  The engine runs your search once.
2.  It takes the top-3 results and "assumes" they are perfect.
3.  It picks the most important new words from those results.
4.  It runs your search again with these new words added.
**Result:** This usually improves **Recall** (finding more relevant docs) but can sometimes cause "topic drift" if the first results were bad.

---

## 5. Evaluation & Results
You tested the engine using the **SETC-60** dataset (60 technical documents, 12 queries).

**Key Metrics to Know:**
*   **P@5 (Precision at 5):** Out of the top 5 results, how many were actually relevant?
*   **MAP (Mean Average Precision):** The "gold standard" metric for overall ranking quality.
*   **nDCG@10:** Measures how well the engine put the *best* results at the very top.

**The Conclusion:** **BM25** was your strongest model overall, achieving the highest MAP and nDCG.

---

## 6. Target Venue
The project is framed as a submission to **ACM SIGIR** (Special Interest Group on Information Retrieval). This is the world's leading conference for search engine research.

---

## 7. How to Run & Demo
*   **Web Demo:** `PYTHONPATH=src python web/app.py`
*   **Experiments:** `PYTHONPATH=src python scripts/run_experiments.py`
*   **Tests:** `PYTHONPATH=src python -m unittest discover -s tests`

---

## 8. Quick "Q&A" for the Presentation
*   **Q: Why use a positional index?**
    *   *A: To support phrase queries. Without positions, we only know a doc has 'search' and 'engine', but not if they are next to each other.*
*   **Q: Why is BM25 better than TF-IDF?**
    *   *A: BM25 has "term frequency saturation." It prevents a document from ranking #1 just because it repeats a keyword 100 times.*
*   **Q: What is the main limitation of your study?**
    *   *A: The dataset (SETC-60) is small and synthetic. Future work should use larger public datasets like Cranfield or TREC.*
