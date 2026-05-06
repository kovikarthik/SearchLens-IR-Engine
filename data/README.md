# Data description

This folder contains a self-contained synthetic test collection created for the SearchLens project.

- `documents.jsonl`: 60 short technical documents across 12 search-engine topics.
- `queries.jsonl`: 12 user-style topics.
- `qrels.jsonl`: graded relevance judgments.  A relevance grade of 2 means the document's primary category matches the query topic.  A grade of 1 means the document is intentionally related but not primary.

The dataset is intentionally small so that the index, ranking models, and evaluation metrics can be inspected by hand.  It is not intended to estimate production search quality.
