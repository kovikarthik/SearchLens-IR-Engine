.PHONY: data test experiments search demo clean

data:
	python scripts/create_synthetic_corpus.py

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

experiments:
	PYTHONPATH=src python scripts/run_experiments.py

search:
	PYTHONPATH=src python -m searchlens.cli search --query "bm25 document length normalization" --method bm25 --top-k 5

demo:
	PYTHONPATH=src python web/app.py

clean:
	rm -f outputs/index.json outputs/evaluation.json outputs/metrics.csv outputs/sample_results.json
